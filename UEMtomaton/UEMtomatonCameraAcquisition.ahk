#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

file := FileOpen("InputFileTest.txt", 'r')

Loop, read, InputFileTest.txt
{
    if (%A_Index% = 1)
        fileSavePath := %A_LoopReadLine%
    if (%A_Index% = 2)
        fileNameBase := %A_LoopReadLine%
    if (%A_Index% = 3)
        units := %A_LoopReadLine%
    if (%A_Index% = 7)
        curScanStep := %A_LoopReadLine%
    if (%A_Index% = 8)
        delayText := %A_LoopReadLine%
    if (%A_Index% = 9)
        curScan := %A_LoopReadLine%
    if (%A_Index% = 10)
        acqTime := %A_LoopReadLine%
}

fullImgName = %FileNameBase%_%scannum%_%stepnumber%_%delay%%delayunits%.dm3 ; !!!!!!!!!!!!!!!!!!!!!!!!!!!! not gatan, what image file format that preserves counts?
fullImgPath = %fileSavePath%/%FileNameBase%_%scannum%_%stepnumber%_%delay%%delayunits%.dm3 ; !!!!!!!!!!!!!!!!!!!!!!!!!!!! not gatan, what image file format that preserves counts?

; click to acquire image

sleepTime := acqTime*1000 + 3000
sleep sleepTime 

; save image

; exit AHK script