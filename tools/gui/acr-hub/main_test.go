package main

import (
	"strings"
	"testing"
)

// TestSessionTokenIsNonEmpty はlocalhost API保護tokenが十分な長さで生成されることを確認します。
func TestSessionTokenIsNonEmpty(t *testing.T) {
	token, err := sessionToken()
	if err != nil {
		t.Fatal(err)
	}
	if len(token) != 48 || strings.Trim(token, "0123456789abcdef") != "" {
		t.Fatalf("unexpected token: %q", token)
	}
}
