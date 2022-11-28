HWND hFoundWnd = NULL
WindowSearcher finder
hFoundWnd = finder.FocusWindow()
if (hFoundWnd != NULL):
    # move to foreground
    self.WindowState = System::Windows::Forms::FormWindowState::Minimized
    self.WindowState = System::Windows::Forms::FormWindowState::Normal # self is the dumbest hack I've tried and I'm almost ashamed it works. Almost.
    #SetWindowPos(hWnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE)
    SetForegroundWindowInternal(hFoundWnd)
    #SetActiveWindow(hWnd)
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! RUNUEMSCAN AHK

    time.sleep(0.03)

    self.WindowState = System::Windows::Forms::FormWindowState::Minimized
    self.WindowState = System::Windows::Forms::FormWindowState::Normal # facepalm
else:
    upStat = "Window containing DigitalMicrograph title was not found.\r\n"
    self.camStat.insert(upStat)

def SetForegroundWindowInternal(HWND hWnd):
        if (!::IsWindow(hWnd)):
            return

        BYTE keyState[256] = { 0 }
        #to unlock SetForegroundWindow we need to imitate Alt pressing
        if (::GetKeyboardState((LPBYTE)& keyState)):
            if (!(keyState[VK_MENU] & 0x80)):
                ::keybd_event(VK_MENU, 0, KEYEVENTF_EXTENDEDKEY | 0, 0)

        ::SetForegroundWindow(hWnd)

        if (::GetKeyboardState((LPBYTE)& keyState)):
            if (!(keyState[VK_MENU] & 0x80)):
                ::keybd_event(VK_MENU, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
    def PressKey(WORD keypress):
        INPUT input
        WORD vkey = keypress # see link below
        input.type = INPUT_KEYBOARD
        input.ki.wScan = MapVirtualKey(vkey, MAPVK_VK_TO_VSC)
        input.ki.time = 0
        input.ki.dwExtraInfo = 0
        input.ki.wVk = vkey
        input.ki.dwFlags = 0 # there is no KEYEVENTF_KEYDOWN
        SendInput(1, &input, sizeof(INPUT))

        System::Threading::Thread::Sleep(30)
        input.ki.dwFlags = KEYEVENTF_KEYUP
        SendInput(1, &input, sizeof(INPUT))
    def PressEnter():
        INPUT ip
        ip.type = INPUT_KEYBOARD
        ip.ki.time = 0
        ip.ki.dwFlags = KEYEVENTF_UNICODE
        ip.ki.wScan = VK_RETURN #VK_RETURN is the code of Return key
        ip.ki.wVk = 0

        ip.ki.dwExtraInfo = 0
        SendInput(1, &ip, sizeof(INPUT))

class WindowSearcher
{

public:
	HWND FocusWindow();
	static BOOL CALLBACK FindTheDesiredWnd(HWND hWnd, LPARAM lParam);

};
extern WindowSearcher finder;
#pragma once
#include "WindowFinder.h"

/*

Purpose: To write to InputFileTest.txt, which passes data from the delay stage to the DM Script.

Parameters:
	String FilePath: Path of InputFileTest.txt
	String FileName: InputFileTest.txt

	int DelayTime: the delay time of the delay stage (sourced from delay stage automation)
	int stepNumber: the current step number (sourced from delay stage automation)
	String dm3path: the path to save images in (sourced from camera computer user input)
	String dm3FN: the file name of the dm3 (sourced from both camera computer user input)
	String delayunits: the units on the delay (sourced from delay stage automation)
	int scannum: the current scan number (sourced from delay stage automation)
	int Lambda: the wavelength of pump used (sourced from camera computer user input)
	int RepRate: the repetition rate used (sourced from camera computer user input)
	int Power: the power of the pump (sourced from camera computer user input)

*/

HWND WindowSearcher::FocusWindow()
{

	HWND hFoundWnd = NULL;
	EnumWindows((WNDENUMPROC)&WindowSearcher::FindTheDesiredWnd, reinterpret_cast<LPARAM>(&hFoundWnd));

	return hFoundWnd;
}

/*
		*/
BOOL CALLBACK WindowSearcher::FindTheDesiredWnd(HWND hWnd, LPARAM lParam)
{
	int length = ::GetWindowTextLength(hWnd);
	TCHAR* windowBuffer;
	windowBuffer = new TCHAR[length + 1];
	memset(windowBuffer, 0, (length + 1) * sizeof(TCHAR));
	GetWindowText(hWnd, windowBuffer, length + 1);
	std::string windowTitle;
	std::wstring wStr = windowBuffer;
	windowTitle = std::string(wStr.begin(), wStr.end());
	std::string checkTitle = "DigitalMicrograph";
	if (windowTitle.find(checkTitle) != std::string::npos)
	{
		*(reinterpret_cast<HWND*>(lParam)) = hWnd;
		return FALSE; // stop enumerating
	}
	return TRUE; // keep enumerating
}