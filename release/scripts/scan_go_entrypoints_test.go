package main

import (
	"os"
	"path/filepath"
	"reflect"
	"testing"
)

// {責務: [writeGoFixture: 指定した構文の検査用ソースを作る], 処理: [1: 親を作る, 2: ソース本文を保存する], 引数: [t: 試験, root: 保存先, name: 相対位置, source: ソース本文], 戻り値: [1: 保存したソースの位置]}
func writeGoFixture(t *testing.T, root, name, source string) string {
	t.Helper()
	path := filepath.Join(root, name)
	if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(source), 0600); err != nil {
		t.Fatal(err)
	}
	return path
}

// {責務: [TestCommandAliasesAndComments: 別名を拾いコメントや文字列の偽コマンドを無視することを確認する], 処理: [1: 別名と偽の分岐を含むソースを作る, 2: 構文上の入口だけを照合する], 引数: [t: 試験], 戻り値: []}
func TestCommandAliasesAndComments(t *testing.T) {
	path := writeGoFixture(t, t.TempDir(), "entry.go", `package main
func main() {
 // case "comment":
 text := "case string:"
 switch os.Args[1] {
 case "two", "one":
 case `+"`raw`"+`:
 default:
 }
 switch text { case "not-a-command": }
}
`)
	entry, err := scanGoFile(path)
	if err != nil || entry == nil || !reflect.DeepEqual(entry.Commands, []string{"one", "raw", "two"}) {
		t.Fatalf("unexpected entry: %+v, %v", entry, err)
	}
}

// {責務: [TestNonliteralAndMalformedSourcesFail: 判定不能なコマンドと壊れた構文を検出する], 処理: [1: 不正なソースを二種類作る, 2: 解析が失敗することを確認する], 引数: [t: 試験], 戻り値: []}
func TestNonliteralAndMalformedSourcesFail(t *testing.T) {
	for _, source := range []string{
		`package main; func main() { switch os.Args[1] { case commandName: } }`,
		`package main; func main(`,
	} {
		path := writeGoFixture(t, t.TempDir(), "entry.go", source)
		if _, err := scanGoFile(path); err == nil {
			t.Fatal("unsupported source was silently accepted")
		}
	}
}

// {責務: [TestTreeFindsEntrypointsOutsideMainFilename: ファイル名に依存せず入口を探し内部試験を除外することを確認する], 処理: [1: 実行入口と除外対象を用意する, 2: 相対位置と空のコマンド一覧を確認する], 引数: [t: 試験], 戻り値: []}
func TestTreeFindsEntrypointsOutsideMainFilename(t *testing.T) {
	root := t.TempDir()
	for _, name := range []string{"tools/bin/entry.go", "tools/new/entry.go", "tools/new/entry_test.go", "tools/new/testdata/main.go"} {
		writeGoFixture(t, root, name, `package main; func main() {}`)
	}
	writeGoFixture(t, root, "tools/library/helper.go", `package library; func helper() {}`)
	entries, err := scanGoTree(root)
	want := []goEntrypoint{{Path: "tools/bin/entry.go", Commands: []string{}}, {Path: "tools/new/entry.go", Commands: []string{}}}
	if err != nil || !reflect.DeepEqual(entries, want) {
		t.Fatalf("unexpected tree: %+v, %v", entries, err)
	}
}
