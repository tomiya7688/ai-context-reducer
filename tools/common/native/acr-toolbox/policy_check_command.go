package main

import (
  "bufio"
  "encoding/json"
  "flag"
  "fmt"
  "os"
  "path/filepath"
  "regexp"
  "sort"
  "strings"
)

type policyRule struct {
  ID string `json:"id"`
  Paths []string `json:"paths"`
  Exclude []string `json:"exclude,omitempty"`
  Severity string `json:"severity"`
  Mode string `json:"mode,omitempty"`
  Forbid string `json:"forbid,omitempty"`
  Require string `json:"require,omitempty"`
  Message string `json:"message,omitempty"`
  Semantic bool `json:"semantic,omitempty"`
}
type policyRuleConfig struct { Rules []policyRule `json:"rules"` }
type policyCheckFinding struct {
  RuleID string `json:"rule_id"`
  Severity string `json:"severity"`
  Path string `json:"path"`
  Line int `json:"line,omitempty"`
  Kind string `json:"kind"`
  Message string `json:"message"`
  Match string `json:"match,omitempty"`
}
type policySuppression struct {
  RuleID string `json:"rule_id"`
  Path string `json:"path"`
  Line int `json:"line"`
  Reason string `json:"reason"`
}

// policyGlobRegex はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func policyGlobRegex(pattern string) (*regexp.Regexp,error) {
  p:=filepath.ToSlash(pattern)
  var b strings.Builder
  b.WriteString("^")
  for i:=0;i<len(p);i++{
    ch:=p[i]
    if ch=='*'{
      if i+1<len(p)&&p[i+1]=='*'{
        i++
        if i+1<len(p)&&p[i+1]=='/' { i++; b.WriteString("(?:.*/)?") } else { b.WriteString(".*") }
      } else { b.WriteString("[^/]*") }
      continue
    }
    if ch=='?' { b.WriteString("[^/]"); continue }
    if strings.ContainsRune(`.+()|[]{}^$\`,rune(ch)){b.WriteByte('\\')}
    b.WriteByte(ch)
  }
  b.WriteString("$")
  return regexp.Compile(b.String())
}

// policyPathMatches はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func policyPathMatches(path string, patterns []string) bool {
  if len(patterns)==0{return true}
  path=filepath.ToSlash(path)
  for _,p:=range patterns{
    rx,err:=policyGlobRegex(p);if err==nil&&rx.MatchString(path){return true}
  }
  return false
}

// policySuppressionReason はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func policySuppressionReason(line, ruleID string)(string,bool,bool){
  marker:="acr-ignore "+ruleID
  i:=strings.Index(line,marker)
  if i<0{return "",false,false}
  tail:=strings.TrimSpace(line[i+len(marker):])
  if strings.HasPrefix(tail,":"){
    reason:=strings.TrimSpace(strings.TrimPrefix(tail,":"))
    if reason!=""{return reason,true,true}
  }
  return "",true,false
}

// policyRuleMatcher はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func policyRuleMatcher(rule policyRule)(func(string)bool,error){
  mode:=rule.Mode;if mode==""{mode="literal"}
  pattern:=rule.Forbid;if pattern==""{pattern=rule.Require}
  switch mode{
  case "literal":
    return func(s string)bool{return strings.Contains(s,pattern)},nil
  case "regex":
    rx,err:=regexp.Compile(pattern);if err!=nil{return nil,err}
    return rx.MatchString,nil
  default:
    return nil,fmt.Errorf("unsupported mode %q",mode)
  }
}

// cmdPolicyCheck は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdPolicyCheck(args []string) int {
  fs:=flag.NewFlagSet("policy-check",flag.ContinueOnError)
  rulesPath:=fs.String("rules","","JSON rule file")
  maxFindings:=fs.Int("max-findings",100,"maximum returned findings; 0 means unlimited")
  if err:=fs.Parse(args);err!=nil{return 2}
  if *rulesPath==""{
    selectorWriteJSON(map[string]any{"tool":"policy-check","status":"invalid_arguments","required_argument":"--rules"})
    return 2
  }
  root:=".";if fs.NArg()>0{root=fs.Arg(0)}
  absRoot,err:=filepath.Abs(root);if err!=nil{return 2}
  data,err:=os.ReadFile(*rulesPath)
  if err!=nil{selectorWriteJSON(map[string]any{"tool":"policy-check","status":"rules_unavailable","rules_path":*rulesPath,"error":boundedErr([]byte(err.Error()))});return 2}
  var cfg policyRuleConfig
  if err:=json.Unmarshal(data,&cfg);err!=nil{selectorWriteJSON(map[string]any{"tool":"policy-check","status":"rules_invalid","rules_path":*rulesPath,"error":boundedErr([]byte(err.Error()))});return 2}

  findings:=[]policyCheckFinding{}; suppressions:=[]policySuppression{}; invalidSuppressions:=[]map[string]any{}; unsupported:=[]map[string]any{}
  filesScanned:=0; readErrors:=[]string{}; ruleErrors:=[]map[string]any{}
  rulesChecked:=0
  for _,rule:=range cfg.Rules{
    if rule.ID==""|| (rule.Forbid==""&&rule.Require==""){
      ruleErrors=append(ruleErrors,map[string]any{"rule_id":rule.ID,"error":"rule requires id and exactly one of forbid/require"})
      continue
    }
    if rule.Forbid!=""&&rule.Require!=""{
      ruleErrors=append(ruleErrors,map[string]any{"rule_id":rule.ID,"error":"rule cannot define both forbid and require"})
      continue
    }
    sev:=rule.Severity;if sev==""{sev="error"}
    if sev!="error"&&sev!="warning"{
      ruleErrors=append(ruleErrors,map[string]any{"rule_id":rule.ID,"error":"severity must be error or warning"})
      continue
    }
    if rule.Semantic{
      unsupported=append(unsupported,map[string]any{"rule_id":rule.ID,"reason":"semantic rule requires AST/semantic backend"})
      continue
    }
    matcher,err:=policyRuleMatcher(rule)
    if err!=nil{
      ruleErrors=append(ruleErrors,map[string]any{"rule_id":rule.ID,"error":err.Error()})
      continue
    }
    rulesChecked++
    _=filepath.WalkDir(absRoot,func(path string,d os.DirEntry,walkErr error)error{
      if walkErr!=nil{return nil}
      if d.IsDir(){if path!=absRoot&&ignoreDirs[strings.ToLower(d.Name())]{return filepath.SkipDir};return nil}
      rel,e:=filepath.Rel(absRoot,path);if e!=nil{return nil};rel=filepath.ToSlash(rel)
      if !policyPathMatches(rel,rule.Paths)||policyPathMatches(rel,rule.Exclude)&&len(rule.Exclude)>0{return nil}
      h,e:=os.Open(path);if e!=nil{readErrors=append(readErrors,rel);return nil};defer h.Close()
      filesScanned++
      scanner:=bufio.NewScanner(h);scanner.Buffer(make([]byte,64*1024),2*1024*1024)
      lines:=[]string{};for scanner.Scan(){lines=append(lines,scanner.Text())}
      if e:=scanner.Err();e!=nil{readErrors=append(readErrors,rel);return nil}
      if rule.Forbid!=""{
        for i,line:=range lines{
          if !matcher(line){continue}
          reason,marked,valid:=policySuppressionReason(line,rule.ID)
          if !marked&&i>0{reason,marked,valid=policySuppressionReason(lines[i-1],rule.ID)}
          if marked{
            if valid{suppressions=append(suppressions,policySuppression{RuleID:rule.ID,Path:rel,Line:i+1,Reason:reason});continue}
            invalidSuppressions=append(invalidSuppressions,map[string]any{"rule_id":rule.ID,"path":rel,"line":i+1,"reason":"suppression requires non-empty reason"})
          }
          msg:=rule.Message;if msg==""{msg="forbidden pattern matched"}
          findings=append(findings,policyCheckFinding{RuleID:rule.ID,Severity:sev,Path:rel,Line:i+1,Kind:"forbidden_pattern",Message:msg,Match:strings.TrimSpace(line)})
        }
      }else{
        found:=false
        for _,line:=range lines{if matcher(line){found=true;break}}
        if !found{
          msg:=rule.Message;if msg==""{msg="required pattern missing"}
          findings=append(findings,policyCheckFinding{RuleID:rule.ID,Severity:sev,Path:rel,Kind:"required_pattern_missing",Message:msg})
        }
      }
      return nil
    })
  }
  sort.Slice(findings,func(i,j int)bool{if findings[i].Path==findings[j].Path{return findings[i].Line<findings[j].Line};return findings[i].Path<findings[j].Path})
  total:=len(findings);truncated:=false
  errors:=0;warnings:=0
  for _,f:=range findings{if f.Severity=="error"{errors++}else{warnings++}}
  if *maxFindings>0&&len(findings)>*maxFindings{findings=findings[:*maxFindings];truncated=true}
  status:="ok"
  if len(ruleErrors)>0||len(readErrors)>0{status="partial"}
  if errors>0{status="violations"}
  selectorWriteJSON(map[string]any{
    "tool":"policy-check","status":status,"root_path":absRoot,"rules_path":*rulesPath,
    "rules_total":len(cfg.Rules),"rules_checked":rulesChecked,"files_scanned":filesScanned,
    "finding_count_total":total,"error_count":errors,"warning_count":warnings,
    "findings":findings,"findings_truncated":truncated,
    "suppressions":suppressions,"invalid_suppressions":invalidSuppressions,
    "unsupported_rules":unsupported,"rule_errors":ruleErrors,"read_error_paths":uniqueSorted(readErrors),
  })
  if errors>0{return 1}
  if len(ruleErrors)>0{return 2}
  return 0
}
