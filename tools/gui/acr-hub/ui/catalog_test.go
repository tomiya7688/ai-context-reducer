package ui

import (
	"reflect"
	"testing"

	"github.com/tomiya7688/ai-context-reducer/tools/gui/acr-hub/backend"
)

// TestRequiredCategories はIssue #26の6分類が欠けないことを確認します。
func TestRequiredCategories(t *testing.T) {
	want := []string{"change-validation", "context-reduction", "policy-maintenance", "project-analysis", "search-structure", "templates"}
	if got := categoryIDs(); !reflect.DeepEqual(got, want) {
		t.Fatalf("categories = %v, want %v", got, want)
	}
}

// TestActionsUsePurposeTitles はprimary titleへCLI tool名を露出しないことを確認します。
func TestActionsUsePurposeTitles(t *testing.T) {
	for _, action := range Actions() {
		if action.Title == "" || action.Description == "" {
			t.Fatalf("action lacks user-facing copy: %+v", action)
		}
		if action.Title == action.TechnicalCommand {
			t.Fatalf("action title exposes technical command: %+v", action)
		}
	}
}

// TestBuildSearchRequest は必要入力だけから既存search CLI契約を組み立てます。
func TestBuildSearchRequest(t *testing.T) {
	request, _, err := buildRequest(RunInput{
		ActionID: "text-search",
		ProjectRoot: "/repo",
		Values: map[string]string{"query": "Service", "glob": "*.go"},
	})
	if err != nil {
		t.Fatal(err)
	}
	want := []string{"search", "--max-results", "50", "--glob", "*.go", "Service", "/repo"}
	if request.Program != backend.ProgramACRToolbox || !reflect.DeepEqual(request.Args, want) {
		t.Fatalf("request = %+v want args=%v", request, want)
	}
}

// TestHeavyBuildKeepsExplicitFlagBoundary は確認済み時だけallow-heavyをCLIへ渡します。
func TestHeavyBuildKeepsExplicitFlagBoundary(t *testing.T) {
	noConfirm, action, err := buildRequest(RunInput{ActionID: "large-run", ProjectRoot: "/repo"})
	if err != nil {
		t.Fatal(err)
	}
	if !action.Heavy || !reflect.DeepEqual(noConfirm.Args, []string{"language-large-run", "/repo"}) || noConfirm.AllowHeavy {
		t.Fatalf("unexpected unconfirmed request: %+v action=%+v", noConfirm, action)
	}

	confirmed, _, err := buildRequest(RunInput{ActionID: "large-run", ProjectRoot: "/repo", AllowHeavy: true})
	if err != nil {
		t.Fatal(err)
	}
	if !reflect.DeepEqual(confirmed.Args, []string{"language-large-run", "--allow-heavy", "/repo"}) || !confirmed.AllowHeavy {
		t.Fatalf("unexpected confirmed request: %+v", confirmed)
	}
}

// TestRequiredFieldValidation は不足入力をCLI起動前に止めます。
func TestRequiredFieldValidation(t *testing.T) {
	_, _, err := buildRequest(RunInput{ActionID: "affected-tests", ProjectRoot: "/repo"})
	if err == nil {
		t.Fatal("expected changed paths validation error")
	}
}
