package main

import (
  "bytes"
  "crypto/sha256"
  "encoding/hex"
  "encoding/json"
  "flag"
  "fmt"
  "os"
  "path/filepath"
  "regexp"
  "sort"
  "strings"
)

type templateStringList []string
// String はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func (s *templateStringList) String() string { return strings.Join(*s,",") }
// Set はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func (s *templateStringList) Set(v string) error { *s=append(*s,v); return nil }

type templateFilePlan struct {
  TemplatePath string `json:"template_path"`
  OutputPath string `json:"output_path"`
  Binary bool `json:"binary"`
  Changed bool `json:"changed"`
  Existing bool `json:"existing"`
  Unresolved []string `json:"unresolved_placeholders"`
  DiffHint map[string]any `json:"diff_hint,omitempty"`
}

var templatePlaceholderRX=regexp.MustCompile(`\{\{\s*([A-Za-z_][A-Za-z0-9_.-]*)\s*\}\}`)

// templateScalar はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func templateScalar(v any)(string,bool){
  switch x:=v.(type){
  case string:return x,true
  case float64:return fmt.Sprintf("%v",x),true
  case bool:if x{return "true",true};return "false",true
  case nil:return "",true
  default:return "",false
  }
}

// templateVariables はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func templateVariables(path string)(map[string]string,[]string,error){
  data,err:=os.ReadFile(path);if err!=nil{return nil,nil,err}
  var raw map[string]any
  if err:=json.Unmarshal(data,&raw);err!=nil{return nil,nil,err}
  out:=map[string]string{};bad:=[]string{}
  for k,v:=range raw{
    if s,ok:=templateScalar(v);ok{out[k]=s}else{bad=append(bad,k)}
  }
  sort.Strings(bad)
  return out,bad,nil
}

// renderTemplateBytes は内部結果を安定した利用者向け出力へ変換します。
func renderTemplateBytes(data []byte,vars map[string]string)([]byte,[]string){
  rendered:=templatePlaceholderRX.ReplaceAllFunc(data,func(m []byte)[]byte{
    sub:=templatePlaceholderRX.FindSubmatch(m)
    if len(sub)<2{return m}
    if v,ok:=vars[string(sub[1])];ok{return []byte(v)}
    return m
  })
  names:=[]string{};seen:=map[string]bool{}
  for _,m:=range templatePlaceholderRX.FindAllSubmatch(rendered,-1){
    if len(m)>1&&!seen[string(m[1])]{seen[string(m[1])]=true;names=append(names,string(m[1]))}
  }
  sort.Strings(names)
  return rendered,names
}

// templateBinary はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func templateBinary(data []byte) bool {
  sample:=data;if len(sample)>4096{sample=sample[:4096]}
  return bytes.IndexByte(sample,0)>=0
}

// templateDiffHint はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func templateDiffHint(oldData,newData []byte)map[string]any{
  if bytes.Equal(oldData,newData){return nil}
  oldLines:=strings.Split(strings.ReplaceAll(string(oldData),"\r\n","\n"),"\n")
  newLines:=strings.Split(strings.ReplaceAll(string(newData),"\r\n","\n"),"\n")
  max:=len(oldLines);if len(newLines)>max{max=len(newLines)}
  for i:=0;i<max;i++{
    oldLine:="";newLine:=""
    if i<len(oldLines){oldLine=oldLines[i]}
    if i<len(newLines){newLine=newLines[i]}
    if oldLine!=newLine{
      if len(oldLine)>160{oldLine=oldLine[:160]}
      if len(newLine)>160{newLine=newLine[:160]}
      return map[string]any{"first_changed_line":i+1,"before":oldLine,"after":newLine,"old_line_count":len(oldLines),"new_line_count":len(newLines)}
    }
  }
  return map[string]any{"old_line_count":len(oldLines),"new_line_count":len(newLines)}
}

// templateMetadataPath はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func templateMetadataPath(out string,isDir bool)string{
  if isDir{return filepath.Join(out,".acr-template.json")}
  return out+".acr-template.json"
}

// cmdTemplate は対象サブコマンドの引数解析・境界I/O・compact出力を統括します。
func cmdTemplate(args []string) int {
  fs:=flag.NewFlagSet("template",flag.ContinueOnError)
  templatePath:=fs.String("template","","template file or directory")
  varsPath:=fs.String("vars","","JSON variables file")
  outPath:=fs.String("out","","output file or directory")
  templateID:=fs.String("template-id","","template identifier")
  templateVersion:=fs.String("template-version","","template version")
  dryRun:=fs.Bool("dry-run",false,"preview without writing")
  check:=fs.Bool("check",false,"verify existing output matches rendered template")
  required:=templateStringList{}
  fs.Var(&required,"required","required variable name; repeatable")
  if err:=fs.Parse(args);err!=nil{return 2}
  if *templatePath==""||*varsPath==""||*outPath==""{
    selectorWriteJSON(map[string]any{"tool":"template","status":"invalid_arguments","required_arguments":[]string{"--template","--vars","--out"}});return 2
  }
  info,err:=os.Stat(*templatePath)
  if err!=nil{selectorWriteJSON(map[string]any{"tool":"template","status":"template_unavailable","template_path":*templatePath,"error":boundedErr([]byte(err.Error()))});return 2}
  vars,badVars,err:=templateVariables(*varsPath)
  if err!=nil{selectorWriteJSON(map[string]any{"tool":"template","status":"variables_invalid","variables_path":*varsPath,"error":boundedErr([]byte(err.Error()))});return 2}
  missing:=[]string{}
  for _,k:=range required{if strings.TrimSpace(vars[k])==""{missing=append(missing,k)}}
  sort.Strings(missing)
  if len(badVars)>0||len(missing)>0{
    selectorWriteJSON(map[string]any{"tool":"template","status":"validation_failed","missing_required_variables":missing,"unsupported_variable_types":badVars});return 2
  }
  varsRaw,_:=os.ReadFile(*varsPath);sum:=sha256.Sum256(varsRaw);varsHash:=hex.EncodeToString(sum[:])

  type pair struct{src,dst,rel string}
  pairs:=[]pair{}
  if info.IsDir(){
    err=filepath.WalkDir(*templatePath,func(path string,d os.DirEntry,e error)error{
      if e!=nil{return e};if d.IsDir(){return nil}
      rel,e:=filepath.Rel(*templatePath,path);if e!=nil{return e}
      pairs=append(pairs,pair{src:path,dst:filepath.Join(*outPath,rel),rel:filepath.ToSlash(rel)});return nil
    })
  }else{
    pairs=append(pairs,pair{src:*templatePath,dst:*outPath,rel:filepath.Base(*templatePath)})
  }
  if err!=nil{selectorWriteJSON(map[string]any{"tool":"template","status":"template_scan_failed","error":boundedErr([]byte(err.Error()))});return 2}
  sort.Slice(pairs,func(i,j int)bool{return pairs[i].rel<pairs[j].rel})

  plans:=[]templateFilePlan{};unresolvedAll:=[]string{};changedCount:=0;missingOutput:=0
  renderedByDst:=map[string][]byte{}
  for _,p:=range pairs{
    data,e:=os.ReadFile(p.src);if e!=nil{selectorWriteJSON(map[string]any{"tool":"template","status":"template_read_failed","path":p.src,"error":boundedErr([]byte(e.Error()))});return 2}
    binary:=templateBinary(data);rendered:=data;unresolved:=[]string{}
    if !binary{rendered,unresolved=renderTemplateBytes(data,vars)}
    existing:=false;changed:=true;var old []byte
    if b,e:=os.ReadFile(p.dst);e==nil{existing=true;old=b;changed=!bytes.Equal(old,rendered)}else{missingOutput++}
    if changed{changedCount++}
    plan:=templateFilePlan{TemplatePath:p.rel,OutputPath:filepath.ToSlash(p.dst),Binary:binary,Changed:changed,Existing:existing,Unresolved:unresolved}
    if existing&&!binary&&changed{plan.DiffHint=templateDiffHint(old,rendered)}
    plans=append(plans,plan);renderedByDst[p.dst]=rendered;unresolvedAll=append(unresolvedAll,unresolved...)
  }
  unresolvedAll=uniqueSorted(unresolvedAll)
  status:="ok";exit:=0
  if len(unresolvedAll)>0{status="validation_failed";exit=2}
  if *check && exit==0 && (changedCount>0||missingOutput>0){status="drift_detected";exit=1}
  wrote:=false
  metadataPath:=templateMetadataPath(*outPath,info.IsDir())
  if !*dryRun && !*check && exit==0{
    for dst,data:=range renderedByDst{
      if e:=os.MkdirAll(filepath.Dir(dst),0755);e!=nil{selectorWriteJSON(map[string]any{"tool":"template","status":"write_failed","path":dst,"error":e.Error()});return 2}
      if e:=os.WriteFile(dst,data,0644);e!=nil{selectorWriteJSON(map[string]any{"tool":"template","status":"write_failed","path":dst,"error":e.Error()});return 2}
    }
    meta:=map[string]any{"template_id":*templateID,"template_version":*templateVersion,"template_path":filepath.ToSlash(*templatePath),"variables_sha256":varsHash,"variable_keys":sortedKeys(vars),"output_path":filepath.ToSlash(*outPath)}
    md,_:=json.MarshalIndent(meta,"","  ");md=append(md,'\n')
    metaErr:=os.MkdirAll(filepath.Dir(metadataPath),0755)
    if metaErr==nil{metaErr=os.WriteFile(metadataPath,md,0644)}
    if metaErr!=nil{selectorWriteJSON(map[string]any{"tool":"template","status":"metadata_write_failed","metadata_path":metadataPath,"error":metaErr.Error()});return 2}
    wrote=true
  }
  selectorWriteJSON(map[string]any{
    "tool":"template","status":status,"mode":map[bool]string{true:"check",false:map[bool]string{true:"dry_run",false:"generate"}[*dryRun]}[*check],
    "template_path":filepath.ToSlash(*templatePath),"output_path":filepath.ToSlash(*outPath),
    "template_id":*templateID,"template_version":*templateVersion,"variables_sha256":varsHash,
    "variable_keys":sortedKeys(vars),"file_count":len(plans),"changed_file_count":changedCount,"missing_output_count":missingOutput,
    "files":plans,"unresolved_placeholders":unresolvedAll,"metadata_path":filepath.ToSlash(metadataPath),"wrote":wrote,
    "advanced_backends":map[string]string{"copier":firstAvailable("copier"),"cookiecutter":firstAvailable("cookiecutter")},
  })
  return exit
}

// sortedKeys はこの責務内の変換・routingを局所化し、呼び出し側のworking setを増やさないための処理です。
func sortedKeys(m map[string]string)[]string{
  keys:=make([]string,0,len(m));for k:=range m{keys=append(keys,k)};sort.Strings(keys);return keys
}
