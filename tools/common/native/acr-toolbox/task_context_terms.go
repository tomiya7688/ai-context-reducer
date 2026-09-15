package main

import "strings"

func contextASCIIWordByte(value byte) bool {
    return value == '_' || value >= 'a' && value <= 'z' || value >= '0' && value <= '9'
}

func contextTermPresent(text, term string) bool {
    if term == "" {
        return false
    }
    nonASCII := false
    for _, r := range term {
        if r > 127 {
            nonASCII = true
            break
        }
    }
    if nonASCII {
        return strings.Contains(text, term)
    }

    start := 0
    for start <= len(text)-len(term) {
        offset := strings.Index(text[start:], term)
        if offset < 0 {
            return false
        }
        index := start + offset
        end := index + len(term)
        beforeOK := index == 0 || !contextASCIIWordByte(text[index-1])
        afterOK := end == len(text) || !contextASCIIWordByte(text[end])
        if beforeOK && afterOK {
            return true
        }
        start = index + 1
    }
    return false
}
