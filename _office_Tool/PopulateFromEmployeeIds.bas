Attribute VB_Name = "Module1"
Option Explicit

'================= 可調整參數 =================
Private Const SHEET_MAIN As String = "名單"            ' 只含「員工編號」的清單表
Private Const SHEET_LOOKUP As String = "Lookup"        ' 可選：員工編號→員工Email 覆寫表

Private Const COL_EMP_ID As String = "員工編號"
Private Const COL_EMP_NAME As String = "員工姓名"
Private Const COL_EMP_EMAIL As String = "員工 email address"
Private Const COL_MGR_ID As String = "直屬主管工號"
Private Const COL_MGR_NAME_ZH As String = "直屬主管中文名字"
Private Const COL_MGR_EMAIL As String = "直屬主管email address"
'================================================

Public Sub PopulateFromEmployeeIds()
    On Error GoTo EH

    Dim ws As Worksheet: Set ws = ThisWorkbook.Worksheets(SHEET_MAIN)
    Dim lastRow As Long: lastRow = LastUsedRow(ws)
    If lastRow < 2 Then
        MsgBox "「名單」沒有可處理的員工編號。", vbExclamation: Exit Sub
    End If

    ' 找欄位 & 建立/清空輸出欄
    Dim cEmpId As Long: cEmpId = FindOrErr(ws, COL_EMP_ID)
    Dim cEmpName As Long:   cEmpName = InsertOrFindColumn(ws, COL_EMP_NAME, cEmpId + 1)
    Dim cEmpEmail As Long:  cEmpEmail = InsertOrFindColumn(ws, COL_EMP_EMAIL, cEmpName + 1)
    Dim cMgrId As Long:     cMgrId = InsertOrFindColumn(ws, COL_MGR_ID, cEmpEmail + 1)
    Dim cMgrNameZh As Long: cMgrNameZh = InsertOrFindColumn(ws, COL_MGR_NAME_ZH, cMgrId + 1)
    Dim cMgrEmail As Long:  cMgrEmail = InsertOrFindColumn(ws, COL_MGR_EMAIL, cMgrNameZh + 1)

    Application.ScreenUpdating = False
    Application.EnableEvents = False
    Dim oldStatus: oldStatus = Application.StatusBar

    ' 1) 先讀名單的員工編號集合
    Dim need As Object: Set need = CreateObject("Scripting.Dictionary")
    Dim r As Long, empId As String
    For r = 2 To lastRow
        empId = Trim$(CStr(ws.Cells(r, cEmpId).Value))
        If empId <> vbNullString Then
            need(LCase$(empId)) = True
        End If
    Next

    If need.Count = 0 Then GoTo CleanExit

    ' 2) 讀 Lookup 覆寫（僅覆寫「員工 email」用）
    Dim dictEmpEmailOverride As Object: Set dictEmpEmailOverride = LoadEmpEmailLookup()

    ' 3) 建立：從 GAL 以 Alias（員工編號）為鍵的索引
    Dim idx As Object: Set idx = BuildAliasIndex(need)
    If idx Is Nothing Or idx.Count = 0 Then
        MsgBox "未能從 GAL 以員工編號（Alias）建立索引，請確認 Exchange 的 Alias 是否為員工編號。", vbExclamation
        GoTo CleanExit
    End If

    ' 4) 回填每一列
    Dim info As Variant
    Dim done As Long, total As Long: total = lastRow - 1
    For r = 2 To lastRow
        empId = Trim$(CStr(ws.Cells(r, cEmpId).Value))
        If empId = vbNullString Then GoTo NextR

        If idx.Exists(LCase$(empId)) Then
            info = idx(LCase$(empId))

            ' 員工姓名（盡量取中文）
            ws.Cells(r, cEmpName).Value = Nz(ExtractChinese(info(0)), info(0))
            ' 員工 email（Lookup 覆寫優先）
            If dictEmpEmailOverride.Exists(LCase$(empId)) Then
                ws.Cells(r, cEmpEmail).Value = dictEmpEmailOverride(LCase$(empId))
            Else
                ws.Cells(r, cEmpEmail).Value = info(1)
            End If
            ' 主管資訊
            ws.Cells(r, cMgrId).Value = info(2)
            ws.Cells(r, cMgrNameZh).Value = Nz(ExtractChinese(info(3)), info(3))
            ws.Cells(r, cMgrEmail).Value = info(4)
        Else
            ' 找不到：清空
            ws.Cells(r, cEmpName).Value = vbNullString
            ws.Cells(r, cEmpEmail).Value = vbNullString
            ws.Cells(r, cMgrId).Value = vbNullString
            ws.Cells(r, cMgrNameZh).Value = vbNullString
            ws.Cells(r, cMgrEmail).Value = vbNullString
        End If

NextR:
        done = done + 1
        If done Mod 25 = 0 Then
            Application.StatusBar = "處理中… " & done & " / " & total
            DoEvents
        End If
    Next r

    ' 5) 列出未配對清單
    OutputUnmatched ws, cEmpId, cEmpEmail, idx

CleanExit:
    Application.ScreenUpdating = True
    Application.EnableEvents = True
    Application.StatusBar = oldStatus
    Exit Sub

EH:
    Application.ScreenUpdating = True
    Application.EnableEvents = True
    MsgBox "執行時發生錯誤：" & Err.Number & " - " & Err.Description, vbCritical
End Sub

'=== 以 Outlook 全公司通訊錄（GAL）建立 Alias（員工編號）索引 ===
' 回傳字典：key = LCase(empId)，value = Array(empDisplayName, empSMTP, mgrAlias, mgrDisplayName, mgrSMTP)
Private Function BuildAliasIndex(ByVal need As Object) As Object
    On Error GoTo EH

    Dim olApp As Object, olNS As Object, gal As Object, entries As Object
    Set olApp = GetOutlookApp()
    If olApp Is Nothing Then Exit Function

    Set olNS = olApp.GetNamespace("MAPI")
    Set gal = olNS.GetGlobalAddressList
    If gal Is Nothing Then Exit Function
    Set entries = gal.AddressEntries
    If entries Is Nothing Then Exit Function

    Dim result As Object: Set result = CreateObject("Scripting.Dictionary")

    Dim ae As Object, ex As Object, mgr As Object
    Dim aliasKey As String, needCnt As Long: needCnt = need.Count

    Dim found As Long: found = 0
    Dim i As Long
    For i = 1 To entries.Count
        Set ae = entries.Item(i)
        If ae Is Nothing Then GoTo ContinueI

        ' 僅處理 ExchangeUser 類型
        If ae.AddressEntryUserType = 0 Or ae.AddressEntryUserType = 5 Then ' 0=olExchangeUser, 5=olExchangeRemoteUser
            Set ex = ae.GetExchangeUser
            If Not ex Is Nothing Then
                aliasKey = LCase$(Trim$(Nz(ex.Alias, vbNullString)))
                If aliasKey <> vbNullString Then
                    If need.Exists(aliasKey) Then
                        ' 主管資訊
                        Set mgr = Nothing
                        On Error Resume Next
                        Set mgr = ex.GetExchangeUserManager
                        On Error GoTo EH

                        Dim mgrAlias As String, mgrName As String, mgrSMTP As String
                        If Not mgr Is Nothing Then
                            mgrAlias = Nz(mgr.Alias, "")
                            mgrName = Nz(mgr.Name, "")
                            mgrSMTP = Nz(mgr.PrimarySmtpAddress, "")
                        End If

                        result(aliasKey) = Array( _
                            Nz(ex.Name, ""), _
                            Nz(ex.PrimarySmtpAddress, ""), _
                            Nz(mgrAlias, ""), _
                            Nz(mgrName, ""), _
                            Nz(mgrSMTP, "") _
                        )

                        found = found + 1
                        If found >= needCnt Then Exit For
                    End If
                End If
            End If
        End If

ContinueI:
        ' 繼續
    Next i

    Set BuildAliasIndex = result
    Exit Function
EH:
    Set BuildAliasIndex = Nothing
End Function

'=== 讀取 Lookup 表（員工編號→員工Email 覆寫） ===
Private Function LoadEmpEmailLookup() As Object
    On Error GoTo EH
    Dim dict As Object: Set dict = CreateObject("Scripting.Dictionary")

    Dim ws As Worksheet
    On Error Resume Next: Set ws = ThisWorkbook.Worksheets(SHEET_LOOKUP): On Error GoTo EH
    If ws Is Nothing Then Set LoadEmpEmailLookup = dict: Exit Function

    Dim cId As Long, cMail As Long
    cId = FindColumn(ws, COL_EMP_ID)
    cMail = FindColumn(ws, COL_EMP_EMAIL)
    If cId = 0 Or cMail = 0 Then Set LoadEmpEmailLookup = dict: Exit Function

    Dim r As Long, lastRow As Long: lastRow = LastUsedRow(ws)
    For r = 2 To lastRow
        Dim id As String: id = LCase$(Trim$(CStr(ws.Cells(r, cId).Value)))
        Dim em As String: em = Trim$(CStr(ws.Cells(r, cMail).Value))
        If id <> vbNullString And em <> vbNullString Then
            If Not dict.Exists(id) Then dict.Add id, em
        End If
    Next

    Set LoadEmpEmailLookup = dict
    Exit Function
EH:
    Set LoadEmpEmailLookup = CreateObject("Scripting.Dictionary")
End Function

'=== 產出未配對清單 ===
Private Sub OutputUnmatched(ByVal ws As Worksheet, ByVal cEmpId As Long, ByVal cEmpEmail As Long, ByVal idx As Object)
    Dim wu As Worksheet
    On Error Resume Next
    Set wu = ThisWorkbook.Worksheets("未配對")
    On Error GoTo 0
    If wu Is Nothing Then
        Set wu = ThisWorkbook.Worksheets.Add(After:=ws)
        wu.Name = "未配對"
    Else
        wu.Cells.Clear
    End If

    wu.Range("A1").Value = COL_EMP_ID
    wu.Range("B1").Value = "原因"
    Dim r As Long, lastRow As Long: lastRow = LastUsedRow(ws)
    Dim outR As Long: outR = 1

    For r = 2 To lastRow
        Dim empId As String: empId = Trim$(CStr(ws.Cells(r, cEmpId).Value))
        If empId <> vbNullString Then
            If Not idx.Exists(LCase$(empId)) Then
                outR = outR + 1
                wu.Cells(outR, 1).Value = empId
                wu.Cells(outR, 2).Value = "GAL 無此 Alias（員工編號）或無法解析"
            End If
        End If
    Next
    wu.Columns("A:B").AutoFit
End Sub

'=== 公用工具 ===
Private Function GetOutlookApp() As Object
    On Error Resume Next
    Set GetOutlookApp = GetObject(, "Outlook.Application")
    If GetOutlookApp Is Nothing Then Set GetOutlookApp = CreateObject("Outlook.Application")
End Function

Private Function FindColumn(ByVal ws As Worksheet, ByVal header As String) As Long
    Dim f As Range
    Set f = ws.Rows(1).Find(What:=header, LookAt:=xlWhole, MatchCase:=False)
    If Not f Is Nothing Then FindColumn = f.Column Else FindColumn = 0
End Function

Private Function FindOrErr(ByVal ws As Worksheet, ByVal header As String) As Long
    Dim c As Long: c = FindColumn(ws, header)
    If c = 0 Then Err.Raise vbObjectError + 1, , "找不到欄位：「" & header & "」"
    FindOrErr = c
End Function

Private Function InsertOrFindColumn(ByVal ws As Worksheet, ByVal header As String, ByVal atCol As Long) As Long
    Dim c As Long: c = FindColumn(ws, header)
    If c = 0 Then
        ws.Columns(atCol).Insert
        ws.Cells(1, atCol).Value = header
        InsertOrFindColumn = atCol
    Else
        ws.Range(ws.Cells(2, c), ws.Cells(LastUsedRow(ws), c)).ClearContents
        InsertOrFindColumn = c
    End If
End Function

Private Function LastUsedRow(ByVal ws As Worksheet) As Long
    On Error Resume Next
    LastUsedRow = ws.Cells.Find(What:="*", LookIn:=xlFormulas, SearchOrder:=xlByRows, _
                                SearchDirection:=xlPrevious).Row
    If LastUsedRow = 0 Then LastUsedRow = 1
End Function

Private Function ExtractChinese(ByVal s As String) As String
    Dim i As Long, ch As String, buf As String
    For i = 1 To Len(s)
        ch = Mid$(s, i, 1)
        If AscW(ch) > 127 Then buf = buf & ch
    Next i
    ExtractChinese = Trim$(buf)
End Function

Private Function Nz(ByVal v As Variant, ByVal def As String) As String
    If IsError(v) Then
        Nz = def
    ElseIf VarType(v) = vbString Then
        Nz = IIf(Len(v) = 0, def, CStr(v))
    ElseIf IsMissing(v) Then
        Nz = def
    ElseIf Trim$(CStr(v)) = vbNullString Then
        Nz = def
    Else
        Nz = CStr(v)
    End If
End Function
