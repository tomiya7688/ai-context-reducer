package ui

import (
	"bytes"
	"context"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/tomiya7688/ai-context-reducer/tools/gui/acr-hub/backend"
)

type fakeInvoker struct {
	result backend.Result
	last   backend.Request
	called int
}

// Invoke はHTTP testでprocessを起動せずRequest routingだけを観測します。
func (fake *fakeInvoker) Invoke(_ context.Context, request backend.Request) backend.Result {
	fake.called++
	fake.last = request
	return fake.result
}

// TestIndexInjectsSessionToken はlocalhost APIへのPOSTに必要なtokenをUIだけへ渡します。
func TestIndexInjectsSessionToken(t *testing.T) {
	handler, err := (Server{Invoker: &fakeInvoker{}, SessionToken: "secret-token"}).Handler()
	if err != nil {
		t.Fatal(err)
	}
	recorder := httptest.NewRecorder()
	request := httptest.NewRequest(http.MethodGet, "/", nil)
	handler.ServeHTTP(recorder, request)
	if recorder.Code != http.StatusOK || !strings.Contains(recorder.Body.String(), "content=\"secret-token\"") {
		t.Fatalf("unexpected index response: code=%d body=%q", recorder.Code, recorder.Body.String())
	}
}

// TestRunRequiresSession は別originから単純POSTされてもCLIを起動しません。
func TestRunRequiresSession(t *testing.T) {
	fake := &fakeInvoker{}
	handler, err := (Server{Invoker: fake, SessionToken: "secret"}).Handler()
	if err != nil {
		t.Fatal(err)
	}
	recorder := httptest.NewRecorder()
	request := httptest.NewRequest(http.MethodPost, "/api/run", bytes.NewBufferString("{\"action_id\":\"project-overview\",\"project_root\":\"/repo\"}"))
	request.Header.Set("Content-Type", "application/json")
	handler.ServeHTTP(recorder, request)
	if recorder.Code != http.StatusForbidden || fake.called != 0 {
		t.Fatalf("unexpected response/calls: code=%d calls=%d", recorder.Code, fake.called)
	}
}

// TestRunRoutesThroughBackend は画面APIが既存CLI requestだけをbackendへ渡します。
func TestRunRoutesThroughBackend(t *testing.T) {
	fake := &fakeInvoker{result: backend.Result{
		State: backend.StateSuccess, OutputKind: backend.OutputJSON, ExitCode: 0, CLIStatus: "ok",
		JSON: json.RawMessage("{\"tool\":\"analyze-and-recommend\",\"status\":\"ok\",\"project_root\":\"/repo\",\"files_scanned\":12}"),
	}}
	handler, err := (Server{Invoker: fake, SessionToken: "secret"}).Handler()
	if err != nil {
		t.Fatal(err)
	}
	recorder := httptest.NewRecorder()
	request := httptest.NewRequest(http.MethodPost, "/api/run", bytes.NewBufferString("{\"action_id\":\"project-overview\",\"project_root\":\"/repo\",\"values\":{}}"))
	request.Header.Set("Content-Type", "application/json")
	request.Header.Set("X-ACR-Session", "secret")
	handler.ServeHTTP(recorder, request)
	if recorder.Code != http.StatusOK || fake.called != 1 {
		t.Fatalf("unexpected response/calls: code=%d calls=%d body=%s", recorder.Code, fake.called, recorder.Body.String())
	}
	if fake.last.Program != backend.ProgramACRToolbox || len(fake.last.Args) != 2 || fake.last.Args[0] != "analyze" {
		t.Fatalf("unexpected backend request: %+v", fake.last)
	}
}

// TestActionsEndpointReturnsPurposeCatalog はbrowserが6カテゴリとaction fieldsを取得できます。
func TestActionsEndpointReturnsPurposeCatalog(t *testing.T) {
	handler, err := (Server{Invoker: &fakeInvoker{}, SessionToken: "secret", InitialProject: "/repo"}).Handler()
	if err != nil {
		t.Fatal(err)
	}
	server := httptest.NewServer(handler)
	defer server.Close()
	response, err := http.Get(server.URL + "/api/actions")
	if err != nil {
		t.Fatal(err)
	}
	defer response.Body.Close()
	raw, _ := io.ReadAll(response.Body)
	if response.StatusCode != http.StatusOK || !bytes.Contains(raw, []byte("\"initial_project\":\"/repo\"")) || !bytes.Contains(raw, []byte("\"Project Analysis\"")) {
		t.Fatalf("unexpected actions response: %s", raw)
	}
}
