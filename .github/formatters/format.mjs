// 指定した変更ファイルだけを扱い、依存物や固定入力を一括変更しない。
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import prettier from 'prettier';

const root = fs.realpathSync(fileURLToPath(new URL('../../', import.meta.url)));
const expectedPrettier = JSON.parse(
  fs.readFileSync(new URL('./package.json', import.meta.url), 'utf8'),
).devDependencies.prettier;
if (prettier.version !== expectedPrettier)
  throw new Error('Install the pinned Prettier dependency with npm ci');
const check = process.argv.includes('--check');
const names = process.argv.slice(2).filter((arg) => arg !== '--check');
if (!names.length)
  throw new Error('Specify the changed files; whole-tree formatting is not supported.');
const files = [
  ...new Set(
    names.map((name) => {
      const file = fs.realpathSync(path.resolve(root, name));
      const relative = path.relative(root, file);
      if (
        relative === '..' ||
        relative.startsWith('..' + path.sep) ||
        path.isAbsolute(relative) ||
        !fs.statSync(file).isFile()
      )
        throw new Error('Format target must be a file inside this repository: ' + name);
      if (
        relative
          .split(path.sep)
          .some((part) =>
            [
              'node_modules',
              'vendor',
              'fixtures',
              'testdata',
              '__pycache__',
              '.git',
              'dist',
              'build',
            ].includes(part),
          )
      )
        throw new Error(
          'Generated files, dependencies and preserved fixtures are excluded: ' + name,
        );
      if (!['.py', '.json', '.yml', '.yaml', '.md', '.mjs', '.js'].includes(path.extname(file)))
        throw new Error('Unsupported formatter target: ' + file);
      return file;
    }),
  ),
];
// 相対位置は呼び出し元によらずリポジトリのルートを基準とする。
const pythonFiles = files.filter((file) => path.extname(file) === '.py');
if (pythonFiles.length) {
  const python = process.env.PYTHON || 'python';
  const wanted = fs.readFileSync(new URL('./requirements.txt', import.meta.url), 'utf8').trim();
  const version = spawnSync(python, ['-m', 'ruff', '--version'], { encoding: 'utf8' });
  if (version.status !== 0 || version.stdout.trim() !== wanted.replace('==', ' '))
    throw new Error('Install the pinned formatter from .github/formatters/requirements.txt');
  const args = [
    '-m',
    'ruff',
    'format',
    '--config',
    path.join(root, '.github/formatters/ruff.toml'),
  ];
  if (check) args.push('--check');
  const result = spawnSync(python, [...args, ...pythonFiles], { stdio: 'inherit', cwd: root });
  if (result.error || result.status !== 0) process.exit(result.status || 1);
}
let failed = false;
const prettierFiles = files.filter((file) => !pythonFiles.includes(file));
for (const file of prettierFiles) {
  if (!['.json', '.yml', '.yaml', '.md', '.mjs', '.js'].includes(path.extname(file)))
    throw new Error('Unsupported formatter target: ' + file);
  const before = fs.readFileSync(file, 'utf8');
  const after = await prettier.format(before, {
    filepath: file,
    printWidth: 100,
    singleQuote: true,
    proseWrap: 'preserve',
    endOfLine: 'lf',
  });
  if (before !== after) {
    if (check) {
      console.error('Formatting required: ' + path.relative(root, file));
      failed = true;
    } else fs.writeFileSync(file, after, 'utf8');
  }
}
console.log(
  'Prettier ' +
    prettier.version +
    (check ? ' check' : ' format') +
    ': ' +
    prettierFiles.length +
    ' explicit files; Ruff: ' +
    pythonFiles.length +
    ' explicit files',
);
if (failed) process.exit(1);
