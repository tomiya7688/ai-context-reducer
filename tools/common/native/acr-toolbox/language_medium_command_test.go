package main

import (
	"os"
	"path/filepath"
	"testing"
)

func writeFixture(t *testing.T, root, name, body string) {
	t.Helper()
	path := filepath.Join(root, filepath.FromSlash(name))
	if err := os.MkdirAll(filepath.Dir(path), 0755); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(path, []byte(body), 0644); err != nil {
		t.Fatal(err)
	}
}

// TestMediumDependencyContracts は各言語固有のanalyzer JSON形状を維持する。
func TestMediumDependencyContracts(t *testing.T) {
	cases := []struct {
		language string
		tool     string
		name     string
		content  string
		rowKey   string
		countKey string
		want     string
	}{
		{"python", "python-import-map", "a.py", "import os, sys as system\nfrom pkg.sub import value\n", "imports", "imports_returned", "pkg.sub"},
		{"csharp", "csharp-project-map", "Demo.csproj", "<Project><ItemGroup><ProjectReference Include=\"../lib/lib.csproj\" /></ItemGroup></Project>", "project_references", "project_count", "../lib/lib.csproj"},
		{"go", "go-import-map", "a.go", "package demo\nimport (\n\"fmt\"\n\"strings\"\n)\n", "imports", "imports_returned", "fmt"},
		{"c", "c-include-map", "a.c", "#include <stdio.h>\n", "includes", "includes_returned", "stdio.h"},
		{"cpp", "cpp-include-map", "a.cpp", "#include \"widget.hpp\"\n", "includes", "includes_returned", "widget.hpp"},
		{"gdscript", "gdscript-dependency-map", "a.gd", "extends \"res://base.gd\"\nvar x = preload(\"res://x.tscn\")\n", "dependencies", "dependencies_returned", "res://x.tscn"},
	}
	for _, tc := range cases {
		t.Run(tc.language, func(t *testing.T) {
			root := t.TempDir()
			writeFixture(t, root, tc.name, tc.content)
			result, err := buildDependencyResult(root, tc.language, tc.tool)
			if err != nil {
				t.Fatal(err)
			}
			if result["tool"] != tc.tool || result["language"] != tc.language {
				t.Fatalf("wrong tool/language identity: %#v", result)
			}
			found := false
			if tc.language == "csharp" {
				projects := result["projects"].([]map[string]any)
				if len(projects) != 1 || result[tc.countKey] != 1 {
					t.Fatalf("wrong project map shape: %#v", result)
				}
				for _, value := range projects[0][tc.rowKey].([]string) {
					found = found || value == tc.want
				}
			} else {
				rows := result["files"].([]map[string]any)
				if len(rows) != 1 || result["files_returned"] != 1 {
					t.Fatalf("wrong file map shape: %#v", result)
				}
				for _, value := range rows[0][tc.rowKey].([]string) {
					found = found || value == tc.want
				}
			}
			if !found {
				t.Fatalf("expected %q in %s: %#v", tc.want, tc.rowKey, result)
			}
			if tc.language == "python" {
				if result["parse_error_count"] != nil || result["parse_check_available"] != false {
					t.Fatalf("native Python parser limitation must be explicit: %#v", result)
				}
			}
			if tc.language == "go" && (result["parse_error_count"] != 0 || result["parse_check_available"] != true) {
				t.Fatalf("Go syntax completeness missing: %#v", result)
			}
		})
	}
}

func TestGoImportParseFailureIsReported(t *testing.T) {
	root := t.TempDir()
	writeFixture(t, root, "broken.go", "package demo\nimport (\n\"fmt\"\n")
	result, err := buildDependencyResult(root, "go", "go-import-map")
	if err != nil {
		t.Fatal(err)
	}
	if result["parse_error_count"] != 1 || result["status"] != "ok_with_warnings" {
		t.Fatalf("parse failure was lost: %#v", result)
	}
}

func TestCSharpSourceListingTruncationMatchesContract(t *testing.T) {
	root := t.TempDir()
	writeFixture(t, root, "Demo.csproj", "<Project />")
	writeFixture(t, root, "A.cs", "class A {}")
	writeFixture(t, root, "B.cs", "class B {}")
	projects, _, err := collectMediumFiles(root, "csharp")
	if err != nil || len(projects) != 1 {
		t.Fatalf("collect projects: %v %#v", err, projects)
	}
	files, total, truncated, _ := sourceFilesForProject(root, projects[0], 1)
	if total != 2 || len(files) != 1 || !truncated {
		t.Fatalf("source file bound mismatch: files=%v total=%d truncated=%v", files, total, truncated)
	}
}
