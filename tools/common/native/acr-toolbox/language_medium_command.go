package main

import (
	"encoding/json"
	"flag"
	"go/parser"
	"go/token"
	"io"
	"os"
	"path/filepath"
	"regexp"
	"sort"
	"strconv"
	"strings"
	"unicode/utf8"
)

const defaultCSharpSourceLimit = 300

var pyImport = regexp.MustCompile(`^\s*import\s+([A-Za-z0-9_\.]+(?:\s+as\s+[A-Za-z_][A-Za-z0-9_]*)?(?:\s*,\s*[A-Za-z0-9_\.]+(?:\s+as\s+[A-Za-z_][A-Za-z0-9_]*)?)*)`)
var pyFrom = regexp.MustCompile(`^\s*from\s+([A-Za-z0-9_\.]+)\s+import\s+`)
var includeLine = regexp.MustCompile(`^\s*#\s*include\s*[<"]([^>"]+)[>"]`)
var gdLoad = regexp.MustCompile(`(?:load|preload)\(\s*["']([^"']+)["']\s*\)`)
var gdExtends = regexp.MustCompile(`^\s*extends\s+["']([^"']+)["']`)
var csProjectRef = regexp.MustCompile(`<ProjectReference\s+Include=["']([^"']+)["']`)

// mediumExtensions は各既存analyzerと同じ対象拡張子を返す。
func mediumExtensions(language string) map[string]bool {
	switch language {
	case "python":
		return map[string]bool{".py": true}
	case "go":
		return map[string]bool{".go": true}
	case "c":
		return map[string]bool{".c": true, ".h": true}
	case "cpp":
		return map[string]bool{".cpp": true, ".cc": true, ".cxx": true, ".hpp": true, ".hh": true, ".hxx": true, ".h": true}
	case "gdscript":
		return map[string]bool{".gd": true}
	}
	return map[string]bool{}
}

// collectMediumFiles はignore directoryを除外し、相対path順で対象sourceを列挙する。
func collectMediumFiles(root, language string) ([]string, int, error) {
	files := []string{}
	walkErrors := 0
	err := filepath.WalkDir(root, func(path string, d os.DirEntry, walkErr error) error {
		if walkErr != nil {
			walkErrors++
			return nil
		}
		if d.IsDir() {
			if path != root && mediumIgnoreDirectory(language, d.Name()) {
				return filepath.SkipDir
			}
			return nil
		}
		ext := strings.ToLower(filepath.Ext(path))
		if language == "csharp" {
			if ext == ".csproj" && !containsBuildDirectory(path, root) {
				files = append(files, path)
			}
		} else if mediumExtensions(language)[ext] {
			files = append(files, path)
		}
		return nil
	})
	sort.Strings(files)
	return files, walkErrors, err
}

// containsBuildDirectory は対象root相対pathにC#の除外directoryが含まれるか判定する。
func containsBuildDirectory(path, root string) bool {
	rel, err := filepath.Rel(root, path)
	if err != nil {
		return true
	}
	for _, part := range strings.Split(filepath.ToSlash(rel), "/") {
		if part == "bin" || part == "obj" {
			return true
		}
	}
	return false
}

// mediumIgnoreDirectory はlanguage別analyzerと同じ除外directoryかを判定する。
func mediumIgnoreDirectory(language, name string) bool {
	lower := strings.ToLower(name)
	switch language {
	case "go":
		return name == ".git" || name == "vendor"
	case "gdscript":
		return lower == ".git" || lower == ".godot" || lower == "build" || lower == "dist" || lower == ".idea" || lower == ".vs"
	case "csharp":
		return name == "bin" || name == "obj"
	default:
		return ignoreDirs[lower]
	}
}

// uniqueSorted は重複dependencyを除き、決定論的な順序へ並べる。
func uniqueSorted(values []string) []string {
	seen := map[string]bool{}
	out := []string{}
	for _, value := range values {
		if value != "" && !seen[value] {
			seen[value] = true
			out = append(out, value)
		}
	}
	sort.Strings(out)
	return out
}

// scanImports はimport map用rowを生成する。Python syntax検査はGo標準libraryでは
// 実行できないため、parse_error_countをunknownにしparse_check_available=falseを出す。
func scanImports(path, language string) (map[string]any, bool, bool) {
	row := map[string]any{"status": "ok"}
	imports := []string{}
	readErr := false
	parseFailed := false
	if language == "go" {
		fset := token.NewFileSet()
		file, err := parser.ParseFile(fset, path, nil, parser.ImportsOnly)
		if err != nil {
			parseFailed = true
			row["status"] = "parse_failed"
			row["error"] = err.Error()
			imports = []string{}
		}
		if file != nil {
			for _, spec := range file.Imports {
				if value, unquoteErr := strconv.Unquote(spec.Path.Value); unquoteErr == nil {
					imports = append(imports, value)
				}
			}
		}
	} else {
		file, err := os.Open(path)
		if err != nil {
			row["status"] = "read_failed"
			row["error"] = err.Error()
			row["imports"] = imports
			return row, false, true
		}
		data, readFileErr := io.ReadAll(file)
		closeErr := file.Close()
		if readFileErr != nil || closeErr != nil || (language == "python" && !utf8.Valid(data)) {
			readErr = true
			row["status"] = "read_failed"
			if readFileErr != nil {
				row["error"] = readFileErr.Error()
			} else if closeErr != nil {
				row["error"] = closeErr.Error()
			} else {
				row["error"] = "source is not valid UTF-8"
			}
		} else if language == "python" {
			for _, line := range strings.Split(string(data), "\n") {
				if m := pyImport.FindStringSubmatch(line); len(m) > 1 {
					for _, item := range strings.Split(m[1], ",") {
						fields := strings.Fields(item)
						if len(fields) > 0 {
							imports = append(imports, fields[0])
						}
					}
				}
				if m := pyFrom.FindStringSubmatch(line); len(m) > 1 {
					imports = append(imports, m[1])
				}
			}
		}
		if readErr {
			imports = []string{}
		}
	}
	row["imports"] = uniqueSorted(imports)
	return row, parseFailed, readErr
}

// scanDependencyRow は言語固有rowとdependency field名、read失敗状態を返す。
func scanDependencyRow(path, language string) (map[string]any, string, bool) {
	if language == "python" || language == "go" {
		row, _, readErr := scanImports(path, language)
		return row, "imports", readErr
	}
	if language == "csharp" {
		data, err := os.ReadFile(path)
		refs := []string{}
		row := map[string]any{"status": "ok"}
		if err != nil {
			row["status"], row["error"] = "read_failed", err.Error()
			return row, "project_references", true
		}
		for _, match := range csProjectRef.FindAllStringSubmatch(string(data), -1) {
			if len(match) > 1 {
				refs = append(refs, filepath.ToSlash(match[1]))
			}
		}
		row["project_references"] = uniqueSorted(refs)
		return row, "project_references", false
	}
	data, err := os.ReadFile(path)
	key := "dependencies"
	if language == "c" || language == "cpp" {
		key = "includes"
	}
	row := map[string]any{"status": "ok"}
	values := []string{}
	if err != nil {
		row["status"], row["error"] = "read_failed", err.Error()
		row[key] = values
		return row, key, true
	}
	text := string(data)
	if language == "c" || language == "cpp" {
		for _, line := range strings.Split(text, "\n") {
			if match := includeLine.FindStringSubmatch(line); len(match) > 1 {
				values = append(values, match[1])
			}
		}
	} else if language == "gdscript" {
		for _, match := range gdLoad.FindAllStringSubmatch(text, -1) {
			if len(match) > 1 {
				values = append(values, match[1])
			}
		}
		for _, line := range strings.Split(text, "\n") {
			if match := gdExtends.FindStringSubmatch(line); len(match) > 1 {
				values = append(values, match[1])
			}
		}
	}
	row[key] = uniqueSorted(values)
	return row, key, false
}

// sourceFilesForProject はproject mapで使うC# source一覧とtruncate情報を返す。
func sourceFilesForProject(root, projectPath string, limit int) ([]string, int, bool, int) {
	files := []string{}
	walkErrors := 0
	err := filepath.WalkDir(filepath.Dir(projectPath), func(path string, d os.DirEntry, walkErr error) error {
		if walkErr != nil {
			walkErrors++
			return nil
		}
		if d.IsDir() {
			if path != filepath.Dir(projectPath) && mediumIgnoreDirectory("csharp", d.Name()) {
				return filepath.SkipDir
			}
			return nil
		}
		if strings.EqualFold(filepath.Ext(path), ".cs") && !containsBuildDirectory(path, root) {
			rel, relErr := filepath.Rel(root, path)
			if relErr == nil {
				files = append(files, filepath.ToSlash(rel))
			}
		}
		return nil
	})
	sort.Strings(files)
	total := len(files)
	truncated := limit > 0 && total > limit
	if truncated {
		files = files[:limit]
	}
	return files, total, truncated, walkErrors + boolInt(err != nil)
}

// boolInt はWalkDir失敗をwalk error件数へ加算する値に変換する。
func boolInt(value bool) int {
	if value {
		return 1
	}
	return 0
}

// buildDependencyResult はlanguage固有の既存Medium JSON contractを組み立てる。
func buildDependencyResult(root, language, tool string) (map[string]any, error) {
	files, walkErrors, err := collectMediumFiles(root, language)
	if err != nil {
		return nil, err
	}
	if language == "csharp" {
		projects := []map[string]any{}
		readErrors := 0
		for _, path := range files {
			row, _, readErr := scanDependencyRow(path, language)
			if readErr {
				readErrors++
			}
			sourceFiles, sourceTotal, truncated, sourceWalkErrors := sourceFilesForProject(root, path, defaultCSharpSourceLimit)
			walkErrors += sourceWalkErrors
			rel, _ := filepath.Rel(root, path)
			project := map[string]any{
				"project": filepath.ToSlash(rel), "status": row["status"],
				"project_references": row["project_references"], "source_files": sourceFiles,
				"source_file_count_total": sourceTotal, "source_files_truncated": truncated,
			}
			if message, ok := row["error"]; ok {
				project["error"] = message
			}
			projects = append(projects, project)
		}
		status := "ok"
		if readErrors > 0 || walkErrors > 0 {
			status = "ok_with_warnings"
		}
		return map[string]any{"tool": tool, "status": status, "language": language, "root_path": filepath.ToSlash(root), "projects": projects, "project_count": len(projects), "read_error_count": readErrors, "walk_error_count": walkErrors}, nil
	}

	rows := []map[string]any{}
	readErrors, parseErrors, count := 0, 0, 0
	key := "dependencies"
	if language == "python" || language == "go" {
		key = "imports"
	} else if language == "c" || language == "cpp" {
		key = "includes"
	}
	for _, path := range files {
		row, rowKey, readErr := scanDependencyRow(path, language)
		if rowKey != key {
			return nil, os.ErrInvalid
		}
		if readErr {
			readErrors++
		}
		if language == "go" {
			if row["status"] == "parse_failed" {
				parseErrors++
			}
		}
		count += len(row[key].([]string))
		rel, relErr := filepath.Rel(root, path)
		if relErr == nil {
			row["file"] = filepath.ToSlash(rel)
		}
		rows = append(rows, row)
	}
	status := "ok"
	if readErrors > 0 || parseErrors > 0 || walkErrors > 0 || language == "python" {
		status = "ok_with_warnings"
	}
	result := map[string]any{"tool": tool, "status": status, "language": language, "root_path": filepath.ToSlash(root), "files": rows, "file_count_total": len(files), "files_returned": len(rows), "read_error_count": readErrors, "scan_truncated": false, "walk_error_count": walkErrors}
	switch key {
	case "imports":
		result["imports_returned"] = count
		if language == "go" {
			result["parse_error_count"] = parseErrors
			result["parse_check_available"] = true
		} else {
			result["parse_error_count"] = nil
			result["parse_check_available"] = false
		}
	case "includes":
		result["includes_returned"] = count
	case "dependencies":
		result["dependencies_returned"] = count
	}
	return result, nil
}

// cmdLanguageMediumRun は言語検出、map書き出し、実行結果報告を行う。
func cmdLanguageMediumRun(args []string) int {
	fs := flag.NewFlagSet("language-medium-run", flag.ContinueOnError)
	outDirArg := fs.String("out", ".acr/language-medium", "directory for dependency/project maps")
	if err := fs.Parse(args); err != nil {
		return 2
	}
	root := "."
	if fs.NArg() > 0 {
		root = fs.Arg(0)
	}
	absRoot, err := filepath.Abs(root)
	if err != nil {
		return 2
	}
	walked, err := walkWithOptions(absRoot, false)
	if err != nil {
		selectorWriteJSON(map[string]any{"tool": "language-medium-run", "status": "scan_failed", "error": selectorBoundedText(err.Error(), 800)})
		return 1
	}
	detected := map[string]bool{}
	for _, f := range walked.Files {
		if lang := selectorLanguages[strings.ToLower(filepath.Ext(f.Path))]; lang != "" {
			detected[lang] = true
		}
	}
	outDir := *outDirArg
	if !filepath.IsAbs(outDir) {
		outDir = filepath.Join(absRoot, outDir)
	}
	toolsByLang := map[string]string{"python": "python-import-map", "csharp": "csharp-project-map", "go": "go-import-map", "c": "c-include-map", "cpp": "cpp-include-map", "gdscript": "gdscript-dependency-map"}
	order := []string{"python", "csharp", "go", "c", "cpp", "gdscript"}
	results := []map[string]any{}
	failures := 0
	for _, lang := range order {
		if !detected[lang] {
			continue
		}
		tool := toolsByLang[lang]
		payload, buildErr := buildDependencyResult(absRoot, lang, tool)
		if buildErr != nil {
			results = append(results, map[string]any{"tool_path": tool, "status": "failed", "error": boundedErr([]byte(buildErr.Error()))})
			failures++
			continue
		}
		data, marshalErr := json.MarshalIndent(payload, "", "  ")
		if marshalErr != nil {
			results = append(results, map[string]any{"tool_path": tool, "status": "failed", "error": marshalErr.Error()})
			failures++
			continue
		}
		name := strings.ReplaceAll(strings.ReplaceAll("tools/"+lang+"/medium/"+tool, "/", "_"), "-", "_") + ".json"
		output := filepath.Join(outDir, name)
		if writeErr := writeCommandOutput(output, append(data, '\n')); writeErr != nil {
			results = append(results, map[string]any{"tool_path": tool, "status": "write_failed", "error": writeErr.Error()})
			failures++
			continue
		}
		backend := "acr-toolbox-native-fallback"
		results = append(results, map[string]any{"tool_path": tool, "status": "ok", "backend": backend, "output_path": output, "approximate": lang == "python" || lang == "c" || lang == "cpp" || lang == "gdscript"})
	}
	status := "ok"
	if failures > 0 {
		status = "ok_with_failures"
	}
	selectorWriteJSON(map[string]any{"tool": "language-medium-run", "status": status, "project_root": absRoot, "output_directory": outDir, "results": results, "failure_count": failures})
	if failures > 0 {
		return 1
	}
	return 0
}
