package main

import "testing"

func TestNormalizeSyntaxHealth(t *testing.T) {
    payload := []any{
        map[string]any{"path": "ok.py", "successful": true, "error_count": float64(0), "missing_count": float64(0)},
        map[string]any{"path": "bad.py", "successful": false, "error_count": float64(2), "missing_count": float64(1)},
    }
    rows := normalizeSyntaxHealth(payload)
    if len(rows) != 2 {
        t.Fatalf("expected 2 rows, got %d", len(rows))
    }
    if rows[0].Path != "bad.py" || rows[0].SyntaxOK || rows[0].ErrorCount != 2 || rows[0].MissingCount != 1 {
        t.Fatalf("unexpected failing row: %#v", rows[0])
    }
    if !rows[1].SyntaxOK {
        t.Fatalf("expected ok row: %#v", rows[1])
    }
}

func TestNormalizeSyntaxHealthAlternateFields(t *testing.T) {
    payload := []any{map[string]any{"file": "broken.ts", "errors": float64(1)}}
    rows := normalizeSyntaxHealth(payload)
    if len(rows) != 1 || rows[0].Path != "broken.ts" || rows[0].SyntaxOK {
        t.Fatalf("unexpected row: %#v", rows)
    }
}
