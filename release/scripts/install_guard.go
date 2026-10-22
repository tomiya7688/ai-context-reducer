package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
)

// {責務: [main: 検査対象が呼び出した導入コマンドを記録して拒否する], 処理: [1: 呼び出し名と引数を追記する, 2: 導入処理を実行せず終了する], 引数: [], 戻り値: [], エラー: [記録できない場合も正常終了しない]}
func main() {
	log, err := os.OpenFile(os.Getenv("ACR_INSTALL_GUARD_LOG"), os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0600)
	if err != nil {
		fmt.Fprintln(os.Stderr, "installation guard could not record invocation")
		os.Exit(98)
	}
	err = json.NewEncoder(log).Encode(map[string]any{"command": filepath.Base(os.Args[0]), "args": os.Args[1:]})
	closeErr := log.Close()
	if err != nil || closeErr != nil {
		fmt.Fprintln(os.Stderr, "installation guard could not finish recording")
		os.Exit(98)
	}
	fmt.Fprintln(os.Stderr, "installation command blocked by release gate")
	os.Exit(97)
}
