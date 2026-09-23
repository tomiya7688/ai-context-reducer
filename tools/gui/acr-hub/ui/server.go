package ui

import (
	"context"
	"embed"
	"encoding/json"
	"fmt"
	"io/fs"
	"net/http"
	"strings"

	"github.com/tomiya7688/ai-context-reducer/tools/gui/acr-hub/backend"
)

//go:embed web/*
var webFiles embed.FS

// Invoker は画面をprocess実装から分離しbackend Runnerを差し替え可能にします。
type Invoker interface {
	Invoke(context.Context, backend.Request) backend.Result
}

// Server はstatic GUIとCLI backend APIを同一localhost originで提供します。
type Server struct {
	Invoker        Invoker
	SessionToken   string
	InitialProject string
}

// Handler は埋め込みUIとAPIだけを公開するHTTP handlerを組み立てます。
func (server Server) Handler() (http.Handler, error) {
	if server.Invoker == nil {
		return nil, fmt.Errorf("invoker is required")
	}
	staticFS, err := fs.Sub(webFiles, "web")
	if err != nil {
		return nil, err
	}
	mux := http.NewServeMux()
	mux.HandleFunc("/api/actions", server.handleActions)
	mux.HandleFunc("/api/project-analysis", server.handleProjectAnalysis)
	mux.HandleFunc("/api/run", server.handleRun)
	mux.HandleFunc("/api/health", server.handleHealth)
	mux.HandleFunc("/", server.handleIndex(staticFS))
	return mux, nil
}

// handleHealth はGUI binaryの起動smokeに使える副作用なしendpointです。
func (server Server) handleHealth(writer http.ResponseWriter, request *http.Request) {
	if request.Method != http.MethodGet {
		http.Error(writer, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	writeJSON(writer, http.StatusOK, map[string]any{"status": "ok"})
}

// handleActions は目的別catalogと初期project pathだけを返します。
func (server Server) handleActions(writer http.ResponseWriter, request *http.Request) {
	if request.Method != http.MethodGet {
		http.Error(writer, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	writeJSON(writer, http.StatusOK, map[string]any{
		"categories":      Categories(),
		"actions":         Actions(),
		"initial_project": server.InitialProject,
	})
}

// handleProjectAnalysis はAnalyze -> Selectだけを1操作で実行し候補は自動実行しません。
func (server Server) handleProjectAnalysis(writer http.ResponseWriter, request *http.Request) {
	if request.Method != http.MethodPost {
		http.Error(writer, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	if server.SessionToken == "" || request.Header.Get("X-ACR-Session") != server.SessionToken {
		http.Error(writer, "invalid session", http.StatusForbidden)
		return
	}
	request.Body = http.MaxBytesReader(writer, request.Body, 64*1024)
	var input ProjectAnalysisInput
	decoder := json.NewDecoder(request.Body)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&input); err != nil {
		writeJSON(writer, http.StatusBadRequest, map[string]any{"state": "failure", "error": "invalid request body"})
		return
	}
	view := projectAnalysis(request.Context(), server.Invoker, input.ProjectRoot)
	writeJSON(writer, http.StatusOK, view)
}

// handleRun は固定catalogからRequestを組み立て、既存CLIだけを起動します。
func (server Server) handleRun(writer http.ResponseWriter, request *http.Request) {
	if request.Method != http.MethodPost {
		http.Error(writer, "method not allowed", http.StatusMethodNotAllowed)
		return
	}
	if server.SessionToken == "" || request.Header.Get("X-ACR-Session") != server.SessionToken {
		http.Error(writer, "invalid session", http.StatusForbidden)
		return
	}
	request.Body = http.MaxBytesReader(writer, request.Body, 1024*1024)
	var input RunInput
	decoder := json.NewDecoder(request.Body)
	decoder.DisallowUnknownFields()
	if err := decoder.Decode(&input); err != nil {
		writeJSON(writer, http.StatusBadRequest, map[string]any{"state": "failure", "error": "invalid request body"})
		return
	}
	backendRequest, action, err := buildRequest(input)
	if err != nil {
		writeJSON(writer, http.StatusBadRequest, map[string]any{"state": "failure", "error": err.Error()})
		return
	}
	result := server.Invoker.Invoke(request.Context(), backendRequest)
	view := resultView(result)
	if action.WritesFiles {
		if output := strings.TrimSpace(input.Values["output"]); output != "" {
			view.Summary = append(view.Summary, SummaryItem{Label: "requested_output", Value: output})
		}
	}
	writeJSON(writer, http.StatusOK, map[string]any{
		"action_id": action.ID,
		"title":     action.Title,
		"result":    view,
	})
}

// handleIndex はsession tokenだけをHTMLへ注入し、他assetは埋め込みfileをそのまま返します。
func (server Server) handleIndex(staticFS fs.FS) http.HandlerFunc {
	fileServer := http.FileServer(http.FS(staticFS))
	return func(writer http.ResponseWriter, request *http.Request) {
		if request.URL.Path != "/" && request.URL.Path != "/index.html" {
			fileServer.ServeHTTP(writer, request)
			return
		}
		raw, err := fs.ReadFile(staticFS, "index.html")
		if err != nil {
			http.Error(writer, "UI unavailable", http.StatusInternalServerError)
			return
		}
		html := strings.ReplaceAll(string(raw), "__ACR_SESSION_TOKEN__", server.SessionToken)
		writer.Header().Set("Content-Type", "text/html; charset=utf-8")
		writer.Header().Set("Cache-Control", "no-store")
		_, _ = writer.Write([]byte(html))
	}
}

// writeJSON はAPI responseのcontent typeとencodingを共通化します。
func writeJSON(writer http.ResponseWriter, status int, value any) {
	writer.Header().Set("Content-Type", "application/json; charset=utf-8")
	writer.Header().Set("Cache-Control", "no-store")
	writer.WriteHeader(status)
	_ = json.NewEncoder(writer).Encode(value)
}
