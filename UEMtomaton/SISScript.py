
'''
WriteSIS SISCommWriter

upStat = "Updating DM communication for selective in situe mode.\r\n"
self..insert(upStat)
# UPDATE CAMERA COMMUNICATION DOCUMENT
SISCommWriter.WriteData("C:\\SISFileInput.txt", self.filepathSelInSitu.Text), self.filebaseSelInSitu.Text), str(SIS_images_skipped), str(SIS_total_saves), str(SIS_acq_time)) #"C:\\TestFile\\SISFileInput.txt", self.filepathSelInSitu.Text), self.filebaseSelInSitu.Text), str(SIS_images_skipped), str(SIS_total_saves)

upStat
HWND hFoundWnd = NULL
WindowSearcher finder
hFoundWnd = finder.FocusWindow()
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! SELECTIVE INSITU AHK
if (hFoundWnd != NULL):
    # move to foreground
    self.WindowState = System::Windows::Forms::FormWindowState::Minimized
    self.WindowState = System::Windows::Forms::FormWindowState::Normal # self is the dumbest hack I've tried and I'm almost ashamed it works. Almost.
    SetForegroundWindowInternal(hFoundWnd)
    spawnl(P_NOWAIT, "SelectiveImaging.exe", "SelectiveImaging.exe", NULL)

    System::Threading::Thread::Sleep(30)

    self.WindowState = System::Windows::Forms::FormWindowState::Minimized
    self.WindowState = System::Windows::Forms::FormWindowState::Normal # facepalm
else:
    upStat = "Window containing \"DigitalMicrograph\" title was not found.\r\n")
    self.camStat.insert(upStat)
'''