package main

import (
	"encoding/json"
	"fmt"
	"go/ast"
	"go/parser"
	"go/token"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
)

// {責務: [goEntrypoint: Goの実行入口と直接のサブコマンドを記録する], フィールド: [Path: ソースの相対位置, Commands: 公開コマンド名], 処理: [探索結果をJSONへ渡す]}
type goEntrypoint struct {
	Path     string   `json:"path"`
	Commands []string `json:"commands"`
}

// {責務: [firstArgument: 最初の利用者引数を振り分ける式か判定する], 処理: [1: 添字と参照元を照合する], 引数: [expression: 振り分け対象の式], 戻り値: [1: os.Argsの最初の引数なら真]}
func firstArgument(expression ast.Expr) bool {
	index, ok := expression.(*ast.IndexExpr)
	if !ok {
		return false
	}
	selector, ok := index.X.(*ast.SelectorExpr)
	if !ok {
		return false
	}
	owner, ok := selector.X.(*ast.Ident)
	position, literal := index.Index.(*ast.BasicLit)
	return ok && literal && owner.Name == "os" && selector.Sel.Name == "Args" && position.Kind == token.INT && position.Value == "1"
}

// {責務: [scanGoFile: コメントや文字列を構文と混同せず実行入口を取り出す], 処理: [1: Goの構文を解析する, 2: mainと引数の振り分けを探す, 3: コマンドを整列する], 引数: [path: 解析するソース], 戻り値: [1: 実行入口がある場合の記録, 2: 解析不能ならエラー]}
func scanGoFile(path string) (*goEntrypoint, error) {
	file, err := parser.ParseFile(token.NewFileSet(), path, nil, 0)
	if err != nil || file.Name.Name != "main" {
		return nil, err
	}
	for _, declaration := range file.Decls {
		function, ok := declaration.(*ast.FuncDecl)
		if !ok || function.Recv != nil || function.Name.Name != "main" || function.Body == nil {
			continue
		}
		entry := &goEntrypoint{Path: path, Commands: []string{}}
		ast.Inspect(function.Body, func(node ast.Node) bool {
			dispatch, ok := node.(*ast.SwitchStmt)
			if !ok || !firstArgument(dispatch.Tag) {
				return true
			}
			for _, item := range dispatch.Body.List {
				for _, name := range item.(*ast.CaseClause).List {
					literal, ok := name.(*ast.BasicLit)
					if !ok || literal.Kind != token.STRING {
						err = fmt.Errorf("command name is not a string literal: %s", path)
						continue
					}
					command, decodeErr := strconv.Unquote(literal.Value)
					if decodeErr != nil {
						err = decodeErr
					} else {
						entry.Commands = append(entry.Commands, command)
					}
				}
			}
			return true
		})
		sort.Strings(entry.Commands)
		return entry, err
	}
	return nil, nil
}

// {責務: [scanGoTree: 配布元にあるGoの実行入口を列挙する], 処理: [1: 内部試験や生成先を除外する, 2: Goソースを解析する, 3: 相対位置で結果を整列する], 引数: [root: リポジトリの位置], 戻り値: [1: 実行入口の一覧, 2: 読み込みや構文のエラー]}
func scanGoTree(root string) ([]goEntrypoint, error) {
	entries := []goEntrypoint{}
	err := filepath.WalkDir(filepath.Join(root, "tools"), func(path string, item fs.DirEntry, walkErr error) error {
		if walkErr != nil {
			return walkErr
		}
		name := item.Name()
		if item.IsDir() {
			switch name {
			case "tests", "testdata", "fixtures", "dist", "node_modules", "__pycache__":
				return filepath.SkipDir
			}
			if strings.HasPrefix(name, ".") {
				return filepath.SkipDir
			}
			return nil
		}
		if filepath.Ext(path) != ".go" || strings.HasSuffix(path, "_test.go") {
			return nil
		}
		if item.Type()&os.ModeSymlink != 0 {
			return fmt.Errorf("source symlink is not supported: %s", path)
		}
		entry, err := scanGoFile(path)
		if entry != nil {
			relative, relativeErr := filepath.Rel(root, path)
			if relativeErr != nil {
				return relativeErr
			}
			entry.Path = filepath.ToSlash(relative)
			entries = append(entries, *entry)
		}
		return err
	})
	sort.Slice(entries, func(i, j int) bool { return entries[i].Path < entries[j].Path })
	return entries, err
}

// {責務: [main: 指定リポジトリの探索結果だけを出力する], 処理: [1: 引数を検証する, 2: 探索結果をJSONへ変換する], 引数: [], 戻り値: [], エラー: [失敗時は異常終了する]}
func main() {
	if len(os.Args) != 2 {
		fmt.Fprintln(os.Stderr, "usage: scan-go-entrypoints REPOSITORY")
		os.Exit(2)
	}
	entries, err := scanGoTree(os.Args[1])
	if err == nil {
		err = json.NewEncoder(os.Stdout).Encode(entries)
	}
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}
