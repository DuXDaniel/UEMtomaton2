#pragma once
//#pragma comment (lib, "Ws2_32.lib")
//#pragma comment (lib, "kernel32.lib")
//#pragma comment (lib, "user32.lib")
//#pragma comment (lib, "SoloistC.lib")
//#pragma comment (lib, "SoloistC64.lib")

#include <sys/stat.h>
#include <winsock2.h>
#include <WS2tcpip.h>
#include <process.h> 
#include <iostream>
#include <ctime>
#include <time.h>
#include <sstream>
#include <fstream>
#include <string>
#include <msclr\marshal_cppstd.h>
#include <algorithm>
#include <Windows.h>
#include <WinUser.h>
#include <filesystem>
#include <chrono>       // std::chrono::system_clock
#include <random>       // std::default_random_engine

/* -------------------------------GLOBAL VARIABLE DECLARATIONS-------------------------------------- */

WSADATA WSAData;

// Double socket setup for delay value communication to the camera and run-status communication to the camera
SOCKET dc_server, cc_server;

// Camera side. Two addresses for delay position and camera
SOCKADDR_IN dc_addr, cc_addr;

// Delay stage side. Two clients for delay position communication and camera communication
SOCKET delaycomm_client, camcomm_client;

// Four seperate addresses. Each side of the program will only use two.
SOCKADDR_IN dc_serverAddr, cc_serverAddr, dc_clientAddr, cc_clientAddr;

// variables for passing data between delay stage computer and camera computer. If we need more than 1024 alphanumerical characters, change 1024 to MAX_VAL or integer MAX
char dc_buffer[1024], cc_buffer[1024];

// Indicates the size of the addresses for each communication client and server. Used to open a port
int cc_clientAddrSize, dc_clientAddrSize, servAddrSize;

double SII_acq_time; // selective in situ mode acquisition time
double SII_time_between; // selective in situe mode time skipped between saves
int SII_images_skipped; // selective in situ mode number of images skipped to reach the time skipped required

int SII_total_saves; // selective in situ mode total number of images saved
double SII_total_time; // total time spent saving the images.

double* timeTable; // the table of time points generated from the Make Timepoints program
double* timeptArr; // the array of time points generated from the time-point table
double* expArr; // the array of experimental time points to be measured by the instruments (accounts for randomization)
int includeLast; // indicates whether or not to include the last point in the time-point table
int randomized; // indicates a randomized set of timepoints or not
int totPoints; // the total number of points in the experimental time points array
int delayConnected; // indicates whether or not the delay stage has been connected

int designation; // used to designate whether camera or delay stage after pressing the initialize buttons on either side
int runStat; // indicates the status of a currently running scan. 0 indicates not running. 1 indicates running. 2 indicates a pause. 3 indicates a stop command which will switch to 0.
int repeatValue; // indicates the number of repeat scans there will be in a single run. This will be defaulted to zero to indicate a single pass.
int butPressMeantime; // indicates whether a button has been pressed while a run is occuring (pause, play, or stop 
double timeLeft; // keeps track of the time left in a run. This is an estimated

double spdlght; // m/s
double curZero; // As of August 16th, 2019 position 293.527 mm on the delay stage corresponds to 0 ps
double mm_to_ps;
double curdelTime; // current delay position in terms of time relative to some fixed position on the delay stage

char units[2]; // the units used to designate the file names and .ULG data

// Tracks the time
time_t my_time;

DOUBLE positionFeedback;

// Declaring a namespace and all constructor methods
namespace UEMtomaton {

	using namespace System;
	using namespace System::ComponentModel;
	using namespace System::Collections;
	using namespace System::Windows::Forms;
	using namespace System::Data;
	using namespace System::Drawing;

	public ref class UEMAuto : public System::Windows::Forms::Form
	{
	public:
		UEMAuto(void) // constructor for all values that need to be initialized
		{
			InitializeComponent();

			spdlght = 299792458; // m/s
			mm_to_ps = 1e12 / spdlght / 1000 * 2; // ps/mm, include factor of 2 to account for retroreflector
			units[0] = 'p'; // initialize with ps
			units[1] = 's';
			designation = -1; // to tell either side that no designation has been assigned yet.
			runStat = 0; // set default value of runStat
			repeatValue = 0; // set default value of repeatValue
			timeLeft = 0; // set the estimated time left to zero

			SII_acq_time = -1; // selective in situ mode acquisition time
			SII_time_between = -1; // selective in situe mode time skipped between saves
			SII_images_skipped = 0; // selective in situ mode number of images skipped to reach the time skipped required

			SII_total_saves = -1; // selective in situ mode total number of images saved
			SII_total_time = -1; // total time spent saving the images.

			delayConnected = 0;

			std::string acqTimeZero;
			std::string acqIP;

			std::ifstream OpenFile;

			std::string line;
			int curLine = 0;

			OpenFile.open("UEMtomatonConfig.txt");

			if (OpenFile)
			{

				do
				{

					getline(OpenFile, line);

					if (curLine == 0)
					{
						acqTimeZero = line;
						curLine = 1;
					}
					else if (curLine == 1)
					{
						acqIP = line;
					}

				} while (!OpenFile.eof());

				curZero = std::stod(acqTimeZero);
				this->DelayIPSetting->Text = gcnew String(acqIP.c_str());
				this->servIP->Text = this->DelayIPSetting->Text;

			}
			else
			{

				curZero = 300; /// mm

				this->DelayIPSetting->Text = gcnew String("192.168.0.3");
				this->servIP->Text = this->DelayIPSetting->Text;

				String^ upStat = gcnew String("UEMtomatonConfig.txt not found. Settings set to default values.\r\n");
				this->camStat->AppendText(upStat);

			}

			OpenFile.close();

		}

	protected:
		/// Clean up any resources being used.
		~UEMAuto()
		{
			if (components)
			{
				delete components;
			}
		}

	// Declare all Form objects
	private: System::Windows::Forms::Label^ label1;
	protected:
	private: System::Windows::Forms::ToolStripPanel^ BottomToolStripPanel;
	private: System::Windows::Forms::ToolStripPanel^ TopToolStripPanel;
	private: System::Windows::Forms::ToolStripPanel^ RightToolStripPanel;
	private: System::Windows::Forms::ToolStripPanel^ LeftToolStripPanel;
	private: System::Windows::Forms::ToolStripContentPanel^ ContentPanel;
	private: System::Windows::Forms::TabControl^ cameraTab;

	private: System::Windows::Forms::TabPage^ delayTab;


	private: System::Windows::Forms::Button^ ServInitButton;
	private: System::Windows::Forms::TabPage^ tabPage2;
	private: System::Windows::Forms::Button^ ServConnButton;
	private: System::Windows::Forms::GroupBox^ groupBox1;
	private: System::Windows::Forms::Label^ delayPosTime;




	private: System::Windows::Forms::Label^ label3;
	private: System::Windows::Forms::Label^ label2;



	private: System::Windows::Forms::Label^ delayPosDist;

	private: System::Windows::Forms::Label^ label8;
	private: System::Windows::Forms::Label^ label7;




	private: System::Windows::Forms::TextBox^ statusWindow;









	private: System::Windows::Forms::Button^ disconServ;
	private: System::ComponentModel::BackgroundWorker^ trackTime;

	private: System::Windows::Forms::Label^ curTime;


	private: System::ComponentModel::BackgroundWorker^ delayComm;
	private: System::Windows::Forms::Button^ disconCam;
	private: System::Windows::Forms::TextBox^ servIP;

	private: System::Windows::Forms::Label^ label6;
	private: System::Windows::Forms::Button^ browseFilePath;
	private: System::Windows::Forms::TextBox^ fileSavePath;

	private: System::Windows::Forms::TextBox^ camStat;

	private: System::Windows::Forms::Label^ label9;
	private: System::Windows::Forms::TextBox^ fileNameBase;
	private: System::Windows::Forms::Label^ label10;












	private: System::ComponentModel::BackgroundWorker^ scanRunner;
	private: System::ComponentModel::BackgroundWorker^ cameraRunner;
	private: System::Windows::Forms::Label^ camDelPosPS;
	private: System::Windows::Forms::Label^ camDelPosMM;
	private: System::Windows::Forms::Label^ label12;
	private: System::Windows::Forms::Label^ label11;
	private: System::Windows::Forms::RadioButton^ nsIndicator;

	private: System::Windows::Forms::RadioButton^ psIndicator;
	private: System::ComponentModel::BackgroundWorker^ delayValueUpdater;
	private: System::Windows::Forms::Button^ stopButton;
	private: System::Windows::Forms::Button^ pauseButton;
	private: System::Windows::Forms::Button^ runScan;
	private: System::Windows::Forms::Button^ playRun;
	private: System::Windows::Forms::CheckBox^ randomPoints;
	private: System::Windows::Forms::Button^ MakeTimeButton;
	private: System::Windows::Forms::Label^ timeRemLab;
	private: System::Windows::Forms::DataGridView^ TimePoints;
	private: System::Windows::Forms::DataGridViewTextBoxColumn^ TimepointList;
	private: System::Windows::Forms::Label^ tRT;
	private: System::Windows::Forms::ProgressBar^ runProg;
	private: System::Windows::Forms::DataGridView^ DataReadouts;
	private: System::Windows::Forms::DataGridViewTextBoxColumn^ Step;
	private: System::Windows::Forms::DataGridViewTextBoxColumn^ Timepoint;
	private: System::Windows::Forms::DataGridViewTextBoxColumn^ DelayPos;
	private: System::Windows::Forms::DataGridViewTextBoxColumn^ delayStatus;
private: System::Windows::Forms::TextBox^ RepeatBox;
private: System::Windows::Forms::Label^ RepeatLabel;
private: System::Windows::Forms::TabPage^ tabPage1;


private: System::Windows::Forms::Label^ label5;
private: System::Windows::Forms::TextBox^ DelayIPSetting;

private: System::Windows::Forms::GroupBox^ GeneralSettingsBox;
private: System::Windows::Forms::TextBox^ timeZeroPositionSetting;

private: System::Windows::Forms::Label^ label16;
private: System::Windows::Forms::GroupBox^ DelaySettingsBox;
private: System::Windows::Forms::Label^ label15;
private: System::Windows::Forms::TextBox^ delaySpeedSetting;

private: System::Windows::Forms::GroupBox^ CameraSettingsBox;
private: System::Windows::Forms::Button^ loadSettingsButton;

private: System::Windows::Forms::Button^ DefaultSettingsRestore;
private: System::Windows::Forms::Button^ SaveSettingsButton;
private: System::Windows::Forms::Button^ delayConnect;
private: System::Windows::Forms::TabPage^ tabPage3;
private: System::Windows::Forms::Label^ label13;
private: System::Windows::Forms::TextBox^ SII_total_Time;


private: System::Windows::Forms::Label^ label22;
private: System::Windows::Forms::TextBox^ filebaseSelInSitu;

private: System::Windows::Forms::Label^ label20;
private: System::Windows::Forms::Button^ browseSII;

private: System::Windows::Forms::TextBox^ filepathSelInSitu;

private: System::Windows::Forms::Label^ label21;
private: System::Windows::Forms::Label^ label19;
private: System::Windows::Forms::TextBox^ SII_total_Saves;

private: System::Windows::Forms::Button^ selectiveInSitu;
private: System::Windows::Forms::Label^ label18;
private: System::Windows::Forms::Label^ label17;
private: System::Windows::Forms::Label^ label14;
private: System::Windows::Forms::TextBox^ SII_skipped;
private: System::Windows::Forms::TextBox^ SII_time_Between;
private: System::Windows::Forms::TextBox^ SII_acq_Time;






private: System::Windows::Forms::Label^ label23;
private: System::Windows::Forms::TextBox^ SII_status_box;
private: System::Windows::Forms::Label^ versionNumber;
private: System::Windows::Forms::GroupBox^ groupBox2;

private: System::Windows::Forms::Label^ label25;
private: System::Windows::Forms::TextBox^ customMenuIndex;

private: System::Windows::Forms::Label^ label24;
private: System::Windows::Forms::TextBox^ selectiveInSituIndex;
private: System::Windows::Forms::Label^ label26;
private: System::Windows::Forms::TextBox^ scanScriptIndex;
private: System::Windows::Forms::TextBox^ acqTimeBox;


private: System::Windows::Forms::Label^ label4;










	private: System::ComponentModel::IContainer^ components;
	protected:

	private:
		/// Required designer variable.


#pragma region Windows Form Designer generated code
		/// Required method for Designer support
		void InitializeComponent(void)
		{
			System::Windows::Forms::DataGridViewCellStyle^ dataGridViewCellStyle6 = (gcnew System::Windows::Forms::DataGridViewCellStyle());
			System::Windows::Forms::DataGridViewCellStyle^ dataGridViewCellStyle7 = (gcnew System::Windows::Forms::DataGridViewCellStyle());
			System::Windows::Forms::DataGridViewCellStyle^ dataGridViewCellStyle8 = (gcnew System::Windows::Forms::DataGridViewCellStyle());
			System::Windows::Forms::DataGridViewCellStyle^ dataGridViewCellStyle9 = (gcnew System::Windows::Forms::DataGridViewCellStyle());
			System::Windows::Forms::DataGridViewCellStyle^ dataGridViewCellStyle10 = (gcnew System::Windows::Forms::DataGridViewCellStyle());
			System::ComponentModel::ComponentResourceManager^ resources = (gcnew System::ComponentModel::ComponentResourceManager(UEMAuto::typeid));
			this->label1 = (gcnew System::Windows::Forms::Label());
			this->BottomToolStripPanel = (gcnew System::Windows::Forms::ToolStripPanel());
			this->TopToolStripPanel = (gcnew System::Windows::Forms::ToolStripPanel());
			this->RightToolStripPanel = (gcnew System::Windows::Forms::ToolStripPanel());
			this->LeftToolStripPanel = (gcnew System::Windows::Forms::ToolStripPanel());
			this->ContentPanel = (gcnew System::Windows::Forms::ToolStripContentPanel());
			this->cameraTab = (gcnew System::Windows::Forms::TabControl());
			this->tabPage2 = (gcnew System::Windows::Forms::TabPage());
			this->acqTimeBox = (gcnew System::Windows::Forms::TextBox());
			this->label4 = (gcnew System::Windows::Forms::Label());
			this->RepeatBox = (gcnew System::Windows::Forms::TextBox());
			this->RepeatLabel = (gcnew System::Windows::Forms::Label());
			this->DataReadouts = (gcnew System::Windows::Forms::DataGridView());
			this->Step = (gcnew System::Windows::Forms::DataGridViewTextBoxColumn());
			this->Timepoint = (gcnew System::Windows::Forms::DataGridViewTextBoxColumn());
			this->DelayPos = (gcnew System::Windows::Forms::DataGridViewTextBoxColumn());
			this->delayStatus = (gcnew System::Windows::Forms::DataGridViewTextBoxColumn());
			this->stopButton = (gcnew System::Windows::Forms::Button());
			this->pauseButton = (gcnew System::Windows::Forms::Button());
			this->runScan = (gcnew System::Windows::Forms::Button());
			this->playRun = (gcnew System::Windows::Forms::Button());
			this->randomPoints = (gcnew System::Windows::Forms::CheckBox());
			this->MakeTimeButton = (gcnew System::Windows::Forms::Button());
			this->timeRemLab = (gcnew System::Windows::Forms::Label());
			this->TimePoints = (gcnew System::Windows::Forms::DataGridView());
			this->TimepointList = (gcnew System::Windows::Forms::DataGridViewTextBoxColumn());
			this->tRT = (gcnew System::Windows::Forms::Label());
			this->nsIndicator = (gcnew System::Windows::Forms::RadioButton());
			this->runProg = (gcnew System::Windows::Forms::ProgressBar());
			this->psIndicator = (gcnew System::Windows::Forms::RadioButton());
			this->camDelPosPS = (gcnew System::Windows::Forms::Label());
			this->camDelPosMM = (gcnew System::Windows::Forms::Label());
			this->label12 = (gcnew System::Windows::Forms::Label());
			this->label11 = (gcnew System::Windows::Forms::Label());
			this->fileNameBase = (gcnew System::Windows::Forms::TextBox());
			this->label10 = (gcnew System::Windows::Forms::Label());
			this->browseFilePath = (gcnew System::Windows::Forms::Button());
			this->fileSavePath = (gcnew System::Windows::Forms::TextBox());
			this->camStat = (gcnew System::Windows::Forms::TextBox());
			this->label9 = (gcnew System::Windows::Forms::Label());
			this->servIP = (gcnew System::Windows::Forms::TextBox());
			this->label6 = (gcnew System::Windows::Forms::Label());
			this->disconCam = (gcnew System::Windows::Forms::Button());
			this->ServConnButton = (gcnew System::Windows::Forms::Button());
			this->delayTab = (gcnew System::Windows::Forms::TabPage());
			this->delayConnect = (gcnew System::Windows::Forms::Button());
			this->disconServ = (gcnew System::Windows::Forms::Button());
			this->statusWindow = (gcnew System::Windows::Forms::TextBox());
			this->groupBox1 = (gcnew System::Windows::Forms::GroupBox());
			this->label8 = (gcnew System::Windows::Forms::Label());
			this->label7 = (gcnew System::Windows::Forms::Label());
			this->delayPosDist = (gcnew System::Windows::Forms::Label());
			this->delayPosTime = (gcnew System::Windows::Forms::Label());
			this->label3 = (gcnew System::Windows::Forms::Label());
			this->label2 = (gcnew System::Windows::Forms::Label());
			this->ServInitButton = (gcnew System::Windows::Forms::Button());
			this->tabPage3 = (gcnew System::Windows::Forms::TabPage());
			this->SII_status_box = (gcnew System::Windows::Forms::TextBox());
			this->label23 = (gcnew System::Windows::Forms::Label());
			this->SII_total_Time = (gcnew System::Windows::Forms::TextBox());
			this->label22 = (gcnew System::Windows::Forms::Label());
			this->filebaseSelInSitu = (gcnew System::Windows::Forms::TextBox());
			this->label20 = (gcnew System::Windows::Forms::Label());
			this->browseSII = (gcnew System::Windows::Forms::Button());
			this->filepathSelInSitu = (gcnew System::Windows::Forms::TextBox());
			this->label21 = (gcnew System::Windows::Forms::Label());
			this->label19 = (gcnew System::Windows::Forms::Label());
			this->SII_total_Saves = (gcnew System::Windows::Forms::TextBox());
			this->selectiveInSitu = (gcnew System::Windows::Forms::Button());
			this->label18 = (gcnew System::Windows::Forms::Label());
			this->label17 = (gcnew System::Windows::Forms::Label());
			this->label14 = (gcnew System::Windows::Forms::Label());
			this->SII_skipped = (gcnew System::Windows::Forms::TextBox());
			this->SII_time_Between = (gcnew System::Windows::Forms::TextBox());
			this->SII_acq_Time = (gcnew System::Windows::Forms::TextBox());
			this->label13 = (gcnew System::Windows::Forms::Label());
			this->tabPage1 = (gcnew System::Windows::Forms::TabPage());
			this->groupBox2 = (gcnew System::Windows::Forms::GroupBox());
			this->selectiveInSituIndex = (gcnew System::Windows::Forms::TextBox());
			this->label26 = (gcnew System::Windows::Forms::Label());
			this->scanScriptIndex = (gcnew System::Windows::Forms::TextBox());
			this->label25 = (gcnew System::Windows::Forms::Label());
			this->customMenuIndex = (gcnew System::Windows::Forms::TextBox());
			this->label24 = (gcnew System::Windows::Forms::Label());
			this->loadSettingsButton = (gcnew System::Windows::Forms::Button());
			this->DefaultSettingsRestore = (gcnew System::Windows::Forms::Button());
			this->SaveSettingsButton = (gcnew System::Windows::Forms::Button());
			this->GeneralSettingsBox = (gcnew System::Windows::Forms::GroupBox());
			this->timeZeroPositionSetting = (gcnew System::Windows::Forms::TextBox());
			this->label16 = (gcnew System::Windows::Forms::Label());
			this->DelaySettingsBox = (gcnew System::Windows::Forms::GroupBox());
			this->label15 = (gcnew System::Windows::Forms::Label());
			this->delaySpeedSetting = (gcnew System::Windows::Forms::TextBox());
			this->CameraSettingsBox = (gcnew System::Windows::Forms::GroupBox());
			this->label5 = (gcnew System::Windows::Forms::Label());
			this->DelayIPSetting = (gcnew System::Windows::Forms::TextBox());
			this->trackTime = (gcnew System::ComponentModel::BackgroundWorker());
			this->curTime = (gcnew System::Windows::Forms::Label());
			this->delayComm = (gcnew System::ComponentModel::BackgroundWorker());
			this->scanRunner = (gcnew System::ComponentModel::BackgroundWorker());
			this->cameraRunner = (gcnew System::ComponentModel::BackgroundWorker());
			this->delayValueUpdater = (gcnew System::ComponentModel::BackgroundWorker());
			this->versionNumber = (gcnew System::Windows::Forms::Label());
			this->cameraTab->SuspendLayout();
			this->tabPage2->SuspendLayout();
			(cli::safe_cast<System::ComponentModel::ISupportInitialize^>(this->DataReadouts))->BeginInit();
			(cli::safe_cast<System::ComponentModel::ISupportInitialize^>(this->TimePoints))->BeginInit();
			this->delayTab->SuspendLayout();
			this->groupBox1->SuspendLayout();
			this->tabPage3->SuspendLayout();
			this->tabPage1->SuspendLayout();
			this->groupBox2->SuspendLayout();
			this->GeneralSettingsBox->SuspendLayout();
			this->DelaySettingsBox->SuspendLayout();
			this->CameraSettingsBox->SuspendLayout();
			this->SuspendLayout();
			// 
			// label1
			// 
			this->label1->AutoSize = true;
			this->label1->Font = (gcnew System::Drawing::Font(L"Arial", 14.25F, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->label1->Location = System::Drawing::Point(18, 14);
			this->label1->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label1->Name = L"label1";
			this->label1->Size = System::Drawing::Size(231, 33);
			this->label1->TabIndex = 0;
			this->label1->Text = L"UEM Automation";
			// 
			// BottomToolStripPanel
			// 
			this->BottomToolStripPanel->Location = System::Drawing::Point(0, 0);
			this->BottomToolStripPanel->Name = L"BottomToolStripPanel";
			this->BottomToolStripPanel->Orientation = System::Windows::Forms::Orientation::Horizontal;
			this->BottomToolStripPanel->RowMargin = System::Windows::Forms::Padding(3, 0, 0, 0);
			this->BottomToolStripPanel->Size = System::Drawing::Size(0, 0);
			// 
			// TopToolStripPanel
			// 
			this->TopToolStripPanel->Location = System::Drawing::Point(0, 0);
			this->TopToolStripPanel->Name = L"TopToolStripPanel";
			this->TopToolStripPanel->Orientation = System::Windows::Forms::Orientation::Horizontal;
			this->TopToolStripPanel->RowMargin = System::Windows::Forms::Padding(3, 0, 0, 0);
			this->TopToolStripPanel->Size = System::Drawing::Size(0, 0);
			// 
			// RightToolStripPanel
			// 
			this->RightToolStripPanel->Location = System::Drawing::Point(0, 0);
			this->RightToolStripPanel->Name = L"RightToolStripPanel";
			this->RightToolStripPanel->Orientation = System::Windows::Forms::Orientation::Horizontal;
			this->RightToolStripPanel->RowMargin = System::Windows::Forms::Padding(3, 0, 0, 0);
			this->RightToolStripPanel->Size = System::Drawing::Size(0, 0);
			// 
			// LeftToolStripPanel
			// 
			this->LeftToolStripPanel->Location = System::Drawing::Point(0, 0);
			this->LeftToolStripPanel->Name = L"LeftToolStripPanel";
			this->LeftToolStripPanel->Orientation = System::Windows::Forms::Orientation::Horizontal;
			this->LeftToolStripPanel->RowMargin = System::Windows::Forms::Padding(3, 0, 0, 0);
			this->LeftToolStripPanel->Size = System::Drawing::Size(0, 0);
			// 
			// ContentPanel
			// 
			this->ContentPanel->Size = System::Drawing::Size(1019, 592);
			// 
			// cameraTab
			// 
			this->cameraTab->Controls->Add(this->tabPage2);
			this->cameraTab->Controls->Add(this->delayTab);
			this->cameraTab->Controls->Add(this->tabPage3);
			this->cameraTab->Controls->Add(this->tabPage1);
			this->cameraTab->Location = System::Drawing::Point(24, 83);
			this->cameraTab->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->cameraTab->Name = L"cameraTab";
			this->cameraTab->SelectedIndex = 0;
			this->cameraTab->Size = System::Drawing::Size(1194, 938);
			this->cameraTab->TabIndex = 1;
			// 
			// tabPage2
			// 
			this->tabPage2->Controls->Add(this->acqTimeBox);
			this->tabPage2->Controls->Add(this->label4);
			this->tabPage2->Controls->Add(this->RepeatBox);
			this->tabPage2->Controls->Add(this->RepeatLabel);
			this->tabPage2->Controls->Add(this->DataReadouts);
			this->tabPage2->Controls->Add(this->stopButton);
			this->tabPage2->Controls->Add(this->pauseButton);
			this->tabPage2->Controls->Add(this->runScan);
			this->tabPage2->Controls->Add(this->playRun);
			this->tabPage2->Controls->Add(this->randomPoints);
			this->tabPage2->Controls->Add(this->MakeTimeButton);
			this->tabPage2->Controls->Add(this->timeRemLab);
			this->tabPage2->Controls->Add(this->TimePoints);
			this->tabPage2->Controls->Add(this->tRT);
			this->tabPage2->Controls->Add(this->nsIndicator);
			this->tabPage2->Controls->Add(this->runProg);
			this->tabPage2->Controls->Add(this->psIndicator);
			this->tabPage2->Controls->Add(this->camDelPosPS);
			this->tabPage2->Controls->Add(this->camDelPosMM);
			this->tabPage2->Controls->Add(this->label12);
			this->tabPage2->Controls->Add(this->label11);
			this->tabPage2->Controls->Add(this->fileNameBase);
			this->tabPage2->Controls->Add(this->label10);
			this->tabPage2->Controls->Add(this->browseFilePath);
			this->tabPage2->Controls->Add(this->fileSavePath);
			this->tabPage2->Controls->Add(this->camStat);
			this->tabPage2->Controls->Add(this->label9);
			this->tabPage2->Controls->Add(this->servIP);
			this->tabPage2->Controls->Add(this->label6);
			this->tabPage2->Controls->Add(this->disconCam);
			this->tabPage2->Controls->Add(this->ServConnButton);
			this->tabPage2->Location = System::Drawing::Point(4, 29);
			this->tabPage2->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->tabPage2->Name = L"tabPage2";
			this->tabPage2->Padding = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->tabPage2->Size = System::Drawing::Size(1186, 905);
			this->tabPage2->TabIndex = 1;
			this->tabPage2->Text = L"Camera Side";
			this->tabPage2->UseVisualStyleBackColor = true;
			// 
			// acqTimeBox
			// 
			this->acqTimeBox->Location = System::Drawing::Point(397, 184);
			this->acqTimeBox->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->acqTimeBox->Name = L"acqTimeBox";
			this->acqTimeBox->Size = System::Drawing::Size(50, 26);
			this->acqTimeBox->TabIndex = 26;
			this->acqTimeBox->Text = L"0";
			// 
			// label4
			// 
			this->label4->AutoSize = true;
			this->label4->Location = System::Drawing::Point(287, 187);
			this->label4->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label4->Name = L"label4";
			this->label4->Size = System::Drawing::Size(112, 20);
			this->label4->TabIndex = 25;
			this->label4->Text = L"Acquisition (s):";
			// 
			// RepeatBox
			// 
			this->RepeatBox->Location = System::Drawing::Point(164, 231);
			this->RepeatBox->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->RepeatBox->Name = L"RepeatBox";
			this->RepeatBox->Size = System::Drawing::Size(48, 26);
			this->RepeatBox->TabIndex = 24;
			this->RepeatBox->Text = L"0";
			this->RepeatBox->LostFocus += gcnew System::EventHandler(this, &UEMAuto::RepeatBox_TextChanged);
			// 
			// RepeatLabel
			// 
			this->RepeatLabel->AutoSize = true;
			this->RepeatLabel->Location = System::Drawing::Point(38, 235);
			this->RepeatLabel->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->RepeatLabel->Name = L"RepeatLabel";
			this->RepeatLabel->Size = System::Drawing::Size(115, 20);
			this->RepeatLabel->TabIndex = 23;
			this->RepeatLabel->Text = L"Repeat Scans:";
			// 
			// DataReadouts
			// 
			this->DataReadouts->AllowUserToAddRows = false;
			this->DataReadouts->AllowUserToDeleteRows = false;
			dataGridViewCellStyle6->Alignment = System::Windows::Forms::DataGridViewContentAlignment::MiddleLeft;
			dataGridViewCellStyle6->BackColor = System::Drawing::SystemColors::Control;
			dataGridViewCellStyle6->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 8.25F, System::Drawing::FontStyle::Regular,
				System::Drawing::GraphicsUnit::Point, static_cast<System::Byte>(0)));
			dataGridViewCellStyle6->ForeColor = System::Drawing::SystemColors::WindowText;
			dataGridViewCellStyle6->SelectionBackColor = System::Drawing::SystemColors::Highlight;
			dataGridViewCellStyle6->SelectionForeColor = System::Drawing::SystemColors::HighlightText;
			dataGridViewCellStyle6->WrapMode = System::Windows::Forms::DataGridViewTriState::True;
			this->DataReadouts->ColumnHeadersDefaultCellStyle = dataGridViewCellStyle6;
			this->DataReadouts->ColumnHeadersHeightSizeMode = System::Windows::Forms::DataGridViewColumnHeadersHeightSizeMode::AutoSize;
			this->DataReadouts->Columns->AddRange(gcnew cli::array< System::Windows::Forms::DataGridViewColumn^  >(4) {
				this->Step, this->Timepoint,
					this->DelayPos, this->delayStatus
			});
			dataGridViewCellStyle7->Alignment = System::Windows::Forms::DataGridViewContentAlignment::MiddleLeft;
			dataGridViewCellStyle7->BackColor = System::Drawing::SystemColors::Window;
			dataGridViewCellStyle7->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 8.25F, System::Drawing::FontStyle::Regular,
				System::Drawing::GraphicsUnit::Point, static_cast<System::Byte>(0)));
			dataGridViewCellStyle7->ForeColor = System::Drawing::SystemColors::ControlText;
			dataGridViewCellStyle7->SelectionBackColor = System::Drawing::SystemColors::Highlight;
			dataGridViewCellStyle7->SelectionForeColor = System::Drawing::SystemColors::HighlightText;
			dataGridViewCellStyle7->WrapMode = System::Windows::Forms::DataGridViewTriState::False;
			this->DataReadouts->DefaultCellStyle = dataGridViewCellStyle7;
			this->DataReadouts->Location = System::Drawing::Point(291, 325);
			this->DataReadouts->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->DataReadouts->Name = L"DataReadouts";
			this->DataReadouts->ReadOnly = true;
			dataGridViewCellStyle8->Alignment = System::Windows::Forms::DataGridViewContentAlignment::MiddleLeft;
			dataGridViewCellStyle8->BackColor = System::Drawing::SystemColors::Control;
			dataGridViewCellStyle8->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 8.25F, System::Drawing::FontStyle::Regular,
				System::Drawing::GraphicsUnit::Point, static_cast<System::Byte>(0)));
			dataGridViewCellStyle8->ForeColor = System::Drawing::SystemColors::WindowText;
			dataGridViewCellStyle8->SelectionBackColor = System::Drawing::SystemColors::Highlight;
			dataGridViewCellStyle8->SelectionForeColor = System::Drawing::SystemColors::HighlightText;
			dataGridViewCellStyle8->WrapMode = System::Windows::Forms::DataGridViewTriState::True;
			this->DataReadouts->RowHeadersDefaultCellStyle = dataGridViewCellStyle8;
			this->DataReadouts->RowHeadersWidth = 62;
			this->DataReadouts->Size = System::Drawing::Size(862, 343);
			this->DataReadouts->TabIndex = 8;
			// 
			// Step
			// 
			this->Step->HeaderText = L"Step";
			this->Step->MinimumWidth = 8;
			this->Step->Name = L"Step";
			this->Step->ReadOnly = true;
			this->Step->Width = 150;
			// 
			// Timepoint
			// 
			this->Timepoint->HeaderText = L"Timepoint (ps)";
			this->Timepoint->MinimumWidth = 8;
			this->Timepoint->Name = L"Timepoint";
			this->Timepoint->ReadOnly = true;
			this->Timepoint->Width = 150;
			// 
			// DelayPos
			// 
			this->DelayPos->HeaderText = L"Delay Stage Position (mm)";
			this->DelayPos->MinimumWidth = 8;
			this->DelayPos->Name = L"DelayPos";
			this->DelayPos->ReadOnly = true;
			this->DelayPos->Width = 150;
			// 
			// delayStatus
			// 
			this->delayStatus->HeaderText = L"Status";
			this->delayStatus->MinimumWidth = 8;
			this->delayStatus->Name = L"delayStatus";
			this->delayStatus->ReadOnly = true;
			this->delayStatus->Width = 230;
			// 
			// stopButton
			// 
			this->stopButton->Location = System::Drawing::Point(27, 822);
			this->stopButton->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->stopButton->Name = L"stopButton";
			this->stopButton->Size = System::Drawing::Size(104, 48);
			this->stopButton->TabIndex = 22;
			this->stopButton->Text = L"Stop Run";
			this->stopButton->UseVisualStyleBackColor = true;
			this->stopButton->Click += gcnew System::EventHandler(this, &UEMAuto::StopButton_Click);
			// 
			// pauseButton
			// 
			this->pauseButton->ForeColor = System::Drawing::Color::Black;
			this->pauseButton->Location = System::Drawing::Point(1047, 231);
			this->pauseButton->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->pauseButton->Name = L"pauseButton";
			this->pauseButton->Size = System::Drawing::Size(48, 35);
			this->pauseButton->TabIndex = 21;
			this->pauseButton->Text = L"| |";
			this->pauseButton->UseVisualStyleBackColor = true;
			this->pauseButton->Click += gcnew System::EventHandler(this, &UEMAuto::PauseButton_Click);
			// 
			// runScan
			// 
			this->runScan->Location = System::Drawing::Point(994, 134);
			this->runScan->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->runScan->Name = L"runScan";
			this->runScan->Size = System::Drawing::Size(159, 78);
			this->runScan->TabIndex = 6;
			this->runScan->Text = L"5. Run Scan";
			this->runScan->UseVisualStyleBackColor = true;
			this->runScan->Click += gcnew System::EventHandler(this, &UEMAuto::RunScan_Click);
			// 
			// playRun
			// 
			this->playRun->Location = System::Drawing::Point(1106, 231);
			this->playRun->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->playRun->Name = L"playRun";
			this->playRun->Size = System::Drawing::Size(48, 35);
			this->playRun->TabIndex = 20;
			this->playRun->Text = L">";
			this->playRun->UseVisualStyleBackColor = true;
			this->playRun->Click += gcnew System::EventHandler(this, &UEMAuto::PlayRun_Click);
			// 
			// randomPoints
			// 
			this->randomPoints->AutoSize = true;
			this->randomPoints->Location = System::Drawing::Point(786, 162);
			this->randomPoints->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->randomPoints->Name = L"randomPoints";
			this->randomPoints->Size = System::Drawing::Size(197, 24);
			this->randomPoints->TabIndex = 5;
			this->randomPoints->Text = L"Randomize Timepoints";
			this->randomPoints->UseVisualStyleBackColor = true;
			this->randomPoints->CheckedChanged += gcnew System::EventHandler(this, &UEMAuto::RandomPoints_CheckedChanged);
			// 
			// MakeTimeButton
			// 
			this->MakeTimeButton->Location = System::Drawing::Point(591, 134);
			this->MakeTimeButton->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->MakeTimeButton->Name = L"MakeTimeButton";
			this->MakeTimeButton->Size = System::Drawing::Size(186, 78);
			this->MakeTimeButton->TabIndex = 3;
			this->MakeTimeButton->Text = L"4. Make Timepoints";
			this->MakeTimeButton->UseVisualStyleBackColor = true;
			this->MakeTimeButton->Click += gcnew System::EventHandler(this, &UEMAuto::MakeTimeButton_Click);
			// 
			// timeRemLab
			// 
			this->timeRemLab->AutoSize = true;
			this->timeRemLab->Location = System::Drawing::Point(426, 235);
			this->timeRemLab->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->timeRemLab->Name = L"timeRemLab";
			this->timeRemLab->Size = System::Drawing::Size(55, 20);
			this->timeRemLab->TabIndex = 19;
			this->timeRemLab->Text = L"0 secs";
			// 
			// TimePoints
			// 
			this->TimePoints->AllowUserToAddRows = false;
			this->TimePoints->AllowUserToDeleteRows = false;
			dataGridViewCellStyle9->Alignment = System::Windows::Forms::DataGridViewContentAlignment::MiddleLeft;
			dataGridViewCellStyle9->BackColor = System::Drawing::SystemColors::Control;
			dataGridViewCellStyle9->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 8.25F, System::Drawing::FontStyle::Regular,
				System::Drawing::GraphicsUnit::Point, static_cast<System::Byte>(0)));
			dataGridViewCellStyle9->ForeColor = System::Drawing::SystemColors::WindowText;
			dataGridViewCellStyle9->SelectionBackColor = System::Drawing::SystemColors::Highlight;
			dataGridViewCellStyle9->SelectionForeColor = System::Drawing::SystemColors::HighlightText;
			dataGridViewCellStyle9->WrapMode = System::Windows::Forms::DataGridViewTriState::True;
			this->TimePoints->ColumnHeadersDefaultCellStyle = dataGridViewCellStyle9;
			this->TimePoints->ColumnHeadersHeightSizeMode = System::Windows::Forms::DataGridViewColumnHeadersHeightSizeMode::AutoSize;
			this->TimePoints->Columns->AddRange(gcnew cli::array< System::Windows::Forms::DataGridViewColumn^  >(1) { this->TimepointList });
			dataGridViewCellStyle10->Alignment = System::Windows::Forms::DataGridViewContentAlignment::MiddleLeft;
			dataGridViewCellStyle10->BackColor = System::Drawing::SystemColors::Window;
			dataGridViewCellStyle10->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 8.25F, System::Drawing::FontStyle::Regular,
				System::Drawing::GraphicsUnit::Point, static_cast<System::Byte>(0)));
			dataGridViewCellStyle10->ForeColor = System::Drawing::SystemColors::ControlText;
			dataGridViewCellStyle10->SelectionBackColor = System::Drawing::SystemColors::Highlight;
			dataGridViewCellStyle10->SelectionForeColor = System::Drawing::SystemColors::HighlightText;
			dataGridViewCellStyle10->WrapMode = System::Windows::Forms::DataGridViewTriState::False;
			this->TimePoints->DefaultCellStyle = dataGridViewCellStyle10;
			this->TimePoints->Location = System::Drawing::Point(27, 325);
			this->TimePoints->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->TimePoints->Name = L"TimePoints";
			this->TimePoints->ReadOnly = true;
			this->TimePoints->RowHeadersWidth = 62;
			this->TimePoints->Size = System::Drawing::Size(255, 343);
			this->TimePoints->TabIndex = 4;
			// 
			// TimepointList
			// 
			this->TimepointList->HeaderText = L"Timepoints (ps)";
			this->TimepointList->MinimumWidth = 8;
			this->TimepointList->Name = L"TimepointList";
			this->TimepointList->ReadOnly = true;
			this->TimepointList->Width = 125;
			// 
			// tRT
			// 
			this->tRT->AutoSize = true;
			this->tRT->Location = System::Drawing::Point(222, 235);
			this->tRT->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->tRT->Name = L"tRT";
			this->tRT->Size = System::Drawing::Size(210, 20);
			this->tRT->TabIndex = 18;
			this->tRT->Text = L"Estiimated Time Remaining: ";
			// 
			// nsIndicator
			// 
			this->nsIndicator->AutoSize = true;
			this->nsIndicator->Location = System::Drawing::Point(523, 183);
			this->nsIndicator->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->nsIndicator->Name = L"nsIndicator";
			this->nsIndicator->Size = System::Drawing::Size(51, 24);
			this->nsIndicator->TabIndex = 16;
			this->nsIndicator->Text = L"ns";
			this->nsIndicator->UseVisualStyleBackColor = true;
			this->nsIndicator->CheckedChanged += gcnew System::EventHandler(this, &UEMAuto::NsIndicator_CheckedChanged);
			// 
			// runProg
			// 
			this->runProg->Location = System::Drawing::Point(28, 275);
			this->runProg->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->runProg->Name = L"runProg";
			this->runProg->Size = System::Drawing::Size(1125, 35);
			this->runProg->TabIndex = 17;
			// 
			// psIndicator
			// 
			this->psIndicator->AutoSize = true;
			this->psIndicator->Checked = true;
			this->psIndicator->Location = System::Drawing::Point(471, 183);
			this->psIndicator->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->psIndicator->Name = L"psIndicator";
			this->psIndicator->Size = System::Drawing::Size(51, 24);
			this->psIndicator->TabIndex = 15;
			this->psIndicator->TabStop = true;
			this->psIndicator->Text = L"ps";
			this->psIndicator->UseVisualStyleBackColor = true;
			this->psIndicator->CheckedChanged += gcnew System::EventHandler(this, &UEMAuto::PsIndicator_CheckedChanged);
			// 
			// camDelPosPS
			// 
			this->camDelPosPS->AutoSize = true;
			this->camDelPosPS->Location = System::Drawing::Point(854, 72);
			this->camDelPosPS->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->camDelPosPS->Name = L"camDelPosPS";
			this->camDelPosPS->Size = System::Drawing::Size(36, 20);
			this->camDelPosPS->TabIndex = 14;
			this->camDelPosPS->Text = L"000";
			// 
			// camDelPosMM
			// 
			this->camDelPosMM->AutoSize = true;
			this->camDelPosMM->Location = System::Drawing::Point(854, 34);
			this->camDelPosMM->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->camDelPosMM->Name = L"camDelPosMM";
			this->camDelPosMM->Size = System::Drawing::Size(36, 20);
			this->camDelPosMM->TabIndex = 13;
			this->camDelPosMM->Text = L"000";
			// 
			// label12
			// 
			this->label12->AutoSize = true;
			this->label12->Location = System::Drawing::Point(644, 72);
			this->label12->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label12->Name = L"label12";
			this->label12->Size = System::Drawing::Size(195, 20);
			this->label12->TabIndex = 12;
			this->label12->Text = L"Delay Stage Position (ps): ";
			// 
			// label11
			// 
			this->label11->AutoSize = true;
			this->label11->Location = System::Drawing::Point(644, 34);
			this->label11->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label11->Name = L"label11";
			this->label11->Size = System::Drawing::Size(200, 20);
			this->label11->TabIndex = 11;
			this->label11->Text = L"Delay Stage Position (nm): ";
			// 
			// fileNameBase
			// 
			this->fileNameBase->Location = System::Drawing::Point(165, 182);
			this->fileNameBase->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->fileNameBase->Name = L"fileNameBase";
			this->fileNameBase->Size = System::Drawing::Size(117, 26);
			this->fileNameBase->TabIndex = 9;
			this->fileNameBase->Text = L"Test_01";
			// 
			// label10
			// 
			this->label10->AutoSize = true;
			this->label10->Location = System::Drawing::Point(38, 186);
			this->label10->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label10->Name = L"label10";
			this->label10->Size = System::Drawing::Size(119, 20);
			this->label10->TabIndex = 8;
			this->label10->Text = L"Filename Base:";
			// 
			// browseFilePath
			// 
			this->browseFilePath->Location = System::Drawing::Point(465, 128);
			this->browseFilePath->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->browseFilePath->Name = L"browseFilePath";
			this->browseFilePath->Size = System::Drawing::Size(112, 35);
			this->browseFilePath->TabIndex = 7;
			this->browseFilePath->Text = L"Browse";
			this->browseFilePath->UseVisualStyleBackColor = true;
			this->browseFilePath->Click += gcnew System::EventHandler(this, &UEMAuto::BrowseFilePath_Click);
			// 
			// fileSavePath
			// 
			this->fileSavePath->Location = System::Drawing::Point(117, 131);
			this->fileSavePath->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->fileSavePath->Name = L"fileSavePath";
			this->fileSavePath->Size = System::Drawing::Size(330, 26);
			this->fileSavePath->TabIndex = 6;
			this->fileSavePath->Text = L"C:\\";
			// 
			// camStat
			// 
			this->camStat->Location = System::Drawing::Point(27, 682);
			this->camStat->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->camStat->Multiline = true;
			this->camStat->Name = L"camStat";
			this->camStat->ScrollBars = System::Windows::Forms::ScrollBars::Vertical;
			this->camStat->Size = System::Drawing::Size(1124, 129);
			this->camStat->TabIndex = 5;
			this->camStat->Text = L"Status Bar:\r\n";
			// 
			// label9
			// 
			this->label9->AutoSize = true;
			this->label9->Location = System::Drawing::Point(38, 135);
			this->label9->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label9->Name = L"label9";
			this->label9->Size = System::Drawing::Size(70, 20);
			this->label9->TabIndex = 4;
			this->label9->Text = L"Filepath:";
			// 
			// servIP
			// 
			this->servIP->Location = System::Drawing::Point(452, 49);
			this->servIP->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->servIP->Name = L"servIP";
			this->servIP->Size = System::Drawing::Size(148, 26);
			this->servIP->TabIndex = 3;
			this->servIP->Text = L"192.168.0.3";
			// 
			// label6
			// 
			this->label6->AutoSize = true;
			this->label6->Location = System::Drawing::Point(250, 54);
			this->label6->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label6->Name = L"label6";
			this->label6->Size = System::Drawing::Size(197, 20);
			this->label6->TabIndex = 2;
			this->label6->Text = L"Delay Stage Computer IP: ";
			// 
			// disconCam
			// 
			this->disconCam->Location = System::Drawing::Point(1028, 822);
			this->disconCam->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->disconCam->Name = L"disconCam";
			this->disconCam->Size = System::Drawing::Size(126, 48);
			this->disconCam->TabIndex = 1;
			this->disconCam->Text = L"Disconnect";
			this->disconCam->UseVisualStyleBackColor = true;
			this->disconCam->Click += gcnew System::EventHandler(this, &UEMAuto::DisconCam_Click);
			// 
			// ServConnButton
			// 
			this->ServConnButton->ForeColor = System::Drawing::SystemColors::ControlText;
			this->ServConnButton->Location = System::Drawing::Point(27, 25);
			this->ServConnButton->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->ServConnButton->Name = L"ServConnButton";
			this->ServConnButton->Size = System::Drawing::Size(204, 78);
			this->ServConnButton->TabIndex = 0;
			this->ServConnButton->Text = L"3. Connect to Server";
			this->ServConnButton->UseVisualStyleBackColor = true;
			this->ServConnButton->Click += gcnew System::EventHandler(this, &UEMAuto::ServConnButton_Click);
			// 
			// delayTab
			// 
			this->delayTab->Controls->Add(this->delayConnect);
			this->delayTab->Controls->Add(this->disconServ);
			this->delayTab->Controls->Add(this->statusWindow);
			this->delayTab->Controls->Add(this->groupBox1);
			this->delayTab->Controls->Add(this->ServInitButton);
			this->delayTab->Location = System::Drawing::Point(4, 29);
			this->delayTab->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->delayTab->Name = L"delayTab";
			this->delayTab->Padding = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->delayTab->Size = System::Drawing::Size(1186, 905);
			this->delayTab->TabIndex = 0;
			this->delayTab->Text = L"Delay Stage";
			this->delayTab->UseVisualStyleBackColor = true;
			// 
			// delayConnect
			// 
			this->delayConnect->Location = System::Drawing::Point(27, 25);
			this->delayConnect->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->delayConnect->Name = L"delayConnect";
			this->delayConnect->Size = System::Drawing::Size(176, 78);
			this->delayConnect->TabIndex = 12;
			this->delayConnect->Text = L"1. Connect to \r\nDelay Stage";
			this->delayConnect->UseVisualStyleBackColor = true;
			this->delayConnect->Click += gcnew System::EventHandler(this, &UEMAuto::delayConnect_Click);
			// 
			// disconServ
			// 
			this->disconServ->Location = System::Drawing::Point(962, 25);
			this->disconServ->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->disconServ->Name = L"disconServ";
			this->disconServ->Size = System::Drawing::Size(204, 78);
			this->disconServ->TabIndex = 11;
			this->disconServ->Text = L"Disconnect";
			this->disconServ->UseVisualStyleBackColor = true;
			this->disconServ->Click += gcnew System::EventHandler(this, &UEMAuto::DisconServ_Click);
			// 
			// statusWindow
			// 
			this->statusWindow->Location = System::Drawing::Point(27, 625);
			this->statusWindow->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->statusWindow->Multiline = true;
			this->statusWindow->Name = L"statusWindow";
			this->statusWindow->ScrollBars = System::Windows::Forms::ScrollBars::Vertical;
			this->statusWindow->Size = System::Drawing::Size(1136, 242);
			this->statusWindow->TabIndex = 6;
			this->statusWindow->Text = L"Status Updates:\r\n";
			// 
			// groupBox1
			// 
			this->groupBox1->Controls->Add(this->label8);
			this->groupBox1->Controls->Add(this->label7);
			this->groupBox1->Controls->Add(this->delayPosDist);
			this->groupBox1->Controls->Add(this->delayPosTime);
			this->groupBox1->Controls->Add(this->label3);
			this->groupBox1->Controls->Add(this->label2);
			this->groupBox1->Location = System::Drawing::Point(407, 277);
			this->groupBox1->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->groupBox1->Name = L"groupBox1";
			this->groupBox1->Padding = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->groupBox1->Size = System::Drawing::Size(392, 159);
			this->groupBox1->TabIndex = 2;
			this->groupBox1->TabStop = false;
			this->groupBox1->Text = L"Manual Delay Stage Control";
			// 
			// label8
			// 
			this->label8->AutoSize = true;
			this->label8->Location = System::Drawing::Point(177, 42);
			this->label8->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label8->Name = L"label8";
			this->label8->Size = System::Drawing::Size(107, 20);
			this->label8->TabIndex = 12;
			this->label8->Text = L"Disconnected";
			// 
			// label7
			// 
			this->label7->AutoSize = true;
			this->label7->Location = System::Drawing::Point(22, 42);
			this->label7->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label7->Name = L"label7";
			this->label7->Size = System::Drawing::Size(145, 20);
			this->label7->TabIndex = 11;
			this->label7->Text = L"Connection Status:";
			// 
			// delayPosDist
			// 
			this->delayPosDist->AutoSize = true;
			this->delayPosDist->Location = System::Drawing::Point(141, 122);
			this->delayPosDist->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->delayPosDist->Name = L"delayPosDist";
			this->delayPosDist->Size = System::Drawing::Size(36, 20);
			this->delayPosDist->TabIndex = 9;
			this->delayPosDist->Text = L"000";
			// 
			// delayPosTime
			// 
			this->delayPosTime->AutoSize = true;
			this->delayPosTime->Location = System::Drawing::Point(141, 82);
			this->delayPosTime->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->delayPosTime->Name = L"delayPosTime";
			this->delayPosTime->Size = System::Drawing::Size(36, 20);
			this->delayPosTime->TabIndex = 8;
			this->delayPosTime->Text = L"000";
			// 
			// label3
			// 
			this->label3->AutoSize = true;
			this->label3->Location = System::Drawing::Point(23, 122);
			this->label3->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label3->Name = L"label3";
			this->label3->Size = System::Drawing::Size(109, 20);
			this->label3->TabIndex = 4;
			this->label3->Text = L"Position (mm):";
			// 
			// label2
			// 
			this->label2->AutoSize = true;
			this->label2->Location = System::Drawing::Point(23, 82);
			this->label2->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label2->Name = L"label2";
			this->label2->Size = System::Drawing::Size(100, 20);
			this->label2->TabIndex = 3;
			this->label2->Text = L"Position (ps):";
			// 
			// ServInitButton
			// 
			this->ServInitButton->Location = System::Drawing::Point(212, 25);
			this->ServInitButton->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->ServInitButton->Name = L"ServInitButton";
			this->ServInitButton->Size = System::Drawing::Size(204, 78);
			this->ServInitButton->TabIndex = 0;
			this->ServInitButton->Text = L"2. Initialize Server";
			this->ServInitButton->UseVisualStyleBackColor = true;
			this->ServInitButton->Click += gcnew System::EventHandler(this, &UEMAuto::ServInitButton_Click);
			// 
			// tabPage3
			// 
			this->tabPage3->Controls->Add(this->SII_status_box);
			this->tabPage3->Controls->Add(this->label23);
			this->tabPage3->Controls->Add(this->SII_total_Time);
			this->tabPage3->Controls->Add(this->label22);
			this->tabPage3->Controls->Add(this->filebaseSelInSitu);
			this->tabPage3->Controls->Add(this->label20);
			this->tabPage3->Controls->Add(this->browseSII);
			this->tabPage3->Controls->Add(this->filepathSelInSitu);
			this->tabPage3->Controls->Add(this->label21);
			this->tabPage3->Controls->Add(this->label19);
			this->tabPage3->Controls->Add(this->SII_total_Saves);
			this->tabPage3->Controls->Add(this->selectiveInSitu);
			this->tabPage3->Controls->Add(this->label18);
			this->tabPage3->Controls->Add(this->label17);
			this->tabPage3->Controls->Add(this->label14);
			this->tabPage3->Controls->Add(this->SII_skipped);
			this->tabPage3->Controls->Add(this->SII_time_Between);
			this->tabPage3->Controls->Add(this->SII_acq_Time);
			this->tabPage3->Controls->Add(this->label13);
			this->tabPage3->Location = System::Drawing::Point(4, 29);
			this->tabPage3->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->tabPage3->Name = L"tabPage3";
			this->tabPage3->Padding = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->tabPage3->Size = System::Drawing::Size(1186, 905);
			this->tabPage3->TabIndex = 3;
			this->tabPage3->Text = L"Selective In Situ";
			this->tabPage3->UseVisualStyleBackColor = true;
			// 
			// SII_status_box
			// 
			this->SII_status_box->Location = System::Drawing::Point(310, 597);
			this->SII_status_box->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->SII_status_box->Multiline = true;
			this->SII_status_box->Name = L"SII_status_box";
			this->SII_status_box->ScrollBars = System::Windows::Forms::ScrollBars::Vertical;
			this->SII_status_box->Size = System::Drawing::Size(846, 255);
			this->SII_status_box->TabIndex = 18;
			// 
			// label23
			// 
			this->label23->AutoSize = true;
			this->label23->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 9.75F, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->label23->Location = System::Drawing::Point(36, 343);
			this->label23->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label23->Name = L"label23";
			this->label23->Size = System::Drawing::Size(551, 100);
			this->label23->TabIndex = 3;
			this->label23->Text = resources->GetString(L"label23.Text");
			// 
			// SII_total_Time
			// 
			this->SII_total_Time->Location = System::Drawing::Point(1000, 486);
			this->SII_total_Time->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->SII_total_Time->Name = L"SII_total_Time";
			this->SII_total_Time->ReadOnly = true;
			this->SII_total_Time->Size = System::Drawing::Size(148, 26);
			this->SII_total_Time->TabIndex = 17;
			this->SII_total_Time->Text = L"-1";
			this->SII_total_Time->TextAlign = System::Windows::Forms::HorizontalAlignment::Center;
			// 
			// label22
			// 
			this->label22->AutoSize = true;
			this->label22->Location = System::Drawing::Point(1014, 462);
			this->label22->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label22->Name = L"label22";
			this->label22->Size = System::Drawing::Size(121, 20);
			this->label22->TabIndex = 16;
			this->label22->Text = L"Total Time (sec)";
			this->label22->TextAlign = System::Drawing::ContentAlignment::MiddleCenter;
			// 
			// filebaseSelInSitu
			// 
			this->filebaseSelInSitu->Location = System::Drawing::Point(164, 212);
			this->filebaseSelInSitu->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->filebaseSelInSitu->Name = L"filebaseSelInSitu";
			this->filebaseSelInSitu->Size = System::Drawing::Size(282, 26);
			this->filebaseSelInSitu->TabIndex = 15;
			this->filebaseSelInSitu->Text = L"Test_01";
			// 
			// label20
			// 
			this->label20->AutoSize = true;
			this->label20->Location = System::Drawing::Point(36, 217);
			this->label20->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label20->Name = L"label20";
			this->label20->Size = System::Drawing::Size(119, 20);
			this->label20->TabIndex = 14;
			this->label20->Text = L"Filename Base:";
			// 
			// browseSII
			// 
			this->browseSII->Location = System::Drawing::Point(464, 158);
			this->browseSII->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->browseSII->Name = L"browseSII";
			this->browseSII->Size = System::Drawing::Size(112, 35);
			this->browseSII->TabIndex = 13;
			this->browseSII->Text = L"Browse";
			this->browseSII->UseVisualStyleBackColor = true;
			this->browseSII->Click += gcnew System::EventHandler(this, &UEMAuto::browseSII_Click);
			// 
			// filepathSelInSitu
			// 
			this->filepathSelInSitu->Location = System::Drawing::Point(116, 162);
			this->filepathSelInSitu->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->filepathSelInSitu->Name = L"filepathSelInSitu";
			this->filepathSelInSitu->Size = System::Drawing::Size(330, 26);
			this->filepathSelInSitu->TabIndex = 12;
			this->filepathSelInSitu->Text = L"C:\\";
			// 
			// label21
			// 
			this->label21->AutoSize = true;
			this->label21->Location = System::Drawing::Point(36, 166);
			this->label21->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label21->Name = L"label21";
			this->label21->Size = System::Drawing::Size(70, 20);
			this->label21->TabIndex = 11;
			this->label21->Text = L"Filepath:";
			// 
			// label19
			// 
			this->label19->AutoSize = true;
			this->label19->Location = System::Drawing::Point(36, 462);
			this->label19->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label19->Name = L"label19";
			this->label19->Size = System::Drawing::Size(92, 20);
			this->label19->TabIndex = 10;
			this->label19->Text = L"Total Saves";
			// 
			// SII_total_Saves
			// 
			this->SII_total_Saves->Location = System::Drawing::Point(40, 486);
			this->SII_total_Saves->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->SII_total_Saves->Name = L"SII_total_Saves";
			this->SII_total_Saves->Size = System::Drawing::Size(148, 26);
			this->SII_total_Saves->TabIndex = 9;
			this->SII_total_Saves->Text = L"-1";
			this->SII_total_Saves->LostFocus += gcnew System::EventHandler(this, &UEMAuto::SII_total_Saves_TextChanged);
			// 
			// selectiveInSitu
			// 
			this->selectiveInSitu->Location = System::Drawing::Point(36, 775);
			this->selectiveInSitu->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->selectiveInSitu->Name = L"selectiveInSitu";
			this->selectiveInSitu->Size = System::Drawing::Size(177, 78);
			this->selectiveInSitu->TabIndex = 3;
			this->selectiveInSitu->Text = L"Begin Acquisition";
			this->selectiveInSitu->UseVisualStyleBackColor = true;
			this->selectiveInSitu->Click += gcnew System::EventHandler(this, &UEMAuto::selectiveInSitu_Click);
			// 
			// label18
			// 
			this->label18->AutoSize = true;
			this->label18->Location = System::Drawing::Point(306, 262);
			this->label18->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label18->Name = L"label18";
			this->label18->Size = System::Drawing::Size(124, 20);
			this->label18->TabIndex = 8;
			this->label18->Text = L"Images Skipped";
			// 
			// label17
			// 
			this->label17->AutoSize = true;
			this->label17->Location = System::Drawing::Point(1023, 242);
			this->label17->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label17->Name = L"label17";
			this->label17->Size = System::Drawing::Size(110, 40);
			this->label17->TabIndex = 7;
			this->label17->Text = L"Time Between\r\nSaves (sec)";
			this->label17->TextAlign = System::Drawing::ContentAlignment::MiddleCenter;
			// 
			// label14
			// 
			this->label14->AutoSize = true;
			this->label14->Location = System::Drawing::Point(36, 262);
			this->label14->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label14->Name = L"label14";
			this->label14->Size = System::Drawing::Size(124, 20);
			this->label14->TabIndex = 6;
			this->label14->Text = L"Acquisition Time";
			// 
			// SII_skipped
			// 
			this->SII_skipped->Location = System::Drawing::Point(310, 286);
			this->SII_skipped->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->SII_skipped->Name = L"SII_skipped";
			this->SII_skipped->Size = System::Drawing::Size(148, 26);
			this->SII_skipped->TabIndex = 5;
			this->SII_skipped->Text = L"0";
			this->SII_skipped->LostFocus += gcnew System::EventHandler(this, &UEMAuto::SII_skipped_TextChanged);
			// 
			// SII_time_Between
			// 
			this->SII_time_Between->Location = System::Drawing::Point(1000, 286);
			this->SII_time_Between->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->SII_time_Between->Name = L"SII_time_Between";
			this->SII_time_Between->ReadOnly = true;
			this->SII_time_Between->Size = System::Drawing::Size(148, 26);
			this->SII_time_Between->TabIndex = 4;
			this->SII_time_Between->Text = L"-1";
			this->SII_time_Between->TextAlign = System::Windows::Forms::HorizontalAlignment::Center;
			// 
			// SII_acq_Time
			// 
			this->SII_acq_Time->Location = System::Drawing::Point(40, 286);
			this->SII_acq_Time->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->SII_acq_Time->Name = L"SII_acq_Time";
			this->SII_acq_Time->Size = System::Drawing::Size(148, 26);
			this->SII_acq_Time->TabIndex = 3;
			this->SII_acq_Time->Text = L"-1";
			this->SII_acq_Time->LostFocus += gcnew System::EventHandler(this, &UEMAuto::SII_acq_Time_TextChanged);
			// 
			// label13
			// 
			this->label13->AutoSize = true;
			this->label13->Font = (gcnew System::Drawing::Font(L"Microsoft Sans Serif", 11.25F, System::Drawing::FontStyle::Regular, System::Drawing::GraphicsUnit::Point,
				static_cast<System::Byte>(0)));
			this->label13->Location = System::Drawing::Point(32, 32);
			this->label13->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label13->Name = L"label13";
			this->label13->Size = System::Drawing::Size(1217, 116);
			this->label13->TabIndex = 3;
			this->label13->Text = resources->GetString(L"label13.Text");
			// 
			// tabPage1
			// 
			this->tabPage1->Controls->Add(this->groupBox2);
			this->tabPage1->Controls->Add(this->loadSettingsButton);
			this->tabPage1->Controls->Add(this->DefaultSettingsRestore);
			this->tabPage1->Controls->Add(this->SaveSettingsButton);
			this->tabPage1->Controls->Add(this->GeneralSettingsBox);
			this->tabPage1->Controls->Add(this->DelaySettingsBox);
			this->tabPage1->Controls->Add(this->CameraSettingsBox);
			this->tabPage1->Location = System::Drawing::Point(4, 29);
			this->tabPage1->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->tabPage1->Name = L"tabPage1";
			this->tabPage1->Padding = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->tabPage1->Size = System::Drawing::Size(1186, 905);
			this->tabPage1->TabIndex = 2;
			this->tabPage1->Text = L"Settings";
			this->tabPage1->UseVisualStyleBackColor = true;
			// 
			// groupBox2
			// 
			this->groupBox2->Controls->Add(this->selectiveInSituIndex);
			this->groupBox2->Controls->Add(this->label26);
			this->groupBox2->Controls->Add(this->scanScriptIndex);
			this->groupBox2->Controls->Add(this->label25);
			this->groupBox2->Controls->Add(this->customMenuIndex);
			this->groupBox2->Controls->Add(this->label24);
			this->groupBox2->Location = System::Drawing::Point(22, 199);
			this->groupBox2->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->groupBox2->Name = L"groupBox2";
			this->groupBox2->Padding = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->groupBox2->Size = System::Drawing::Size(412, 163);
			this->groupBox2->TabIndex = 11;
			this->groupBox2->TabStop = false;
			this->groupBox2->Text = L"Script Locations";
			// 
			// selectiveInSituIndex
			// 
			this->selectiveInSituIndex->Location = System::Drawing::Point(332, 112);
			this->selectiveInSituIndex->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->selectiveInSituIndex->Name = L"selectiveInSituIndex";
			this->selectiveInSituIndex->Size = System::Drawing::Size(69, 26);
			this->selectiveInSituIndex->TabIndex = 11;
			this->selectiveInSituIndex->Text = L"4";
			this->selectiveInSituIndex->TextAlign = System::Windows::Forms::HorizontalAlignment::Right;
			// 
			// label26
			// 
			this->label26->AutoSize = true;
			this->label26->Location = System::Drawing::Point(9, 118);
			this->label26->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label26->Name = L"label26";
			this->label26->Size = System::Drawing::Size(207, 20);
			this->label26->TabIndex = 10;
			this->label26->Text = L"Selective InSitu Script Index";
			// 
			// scanScriptIndex
			// 
			this->scanScriptIndex->Location = System::Drawing::Point(332, 71);
			this->scanScriptIndex->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->scanScriptIndex->Name = L"scanScriptIndex";
			this->scanScriptIndex->Size = System::Drawing::Size(69, 26);
			this->scanScriptIndex->TabIndex = 9;
			this->scanScriptIndex->Text = L"2";
			this->scanScriptIndex->TextAlign = System::Windows::Forms::HorizontalAlignment::Right;
			// 
			// label25
			// 
			this->label25->AutoSize = true;
			this->label25->Location = System::Drawing::Point(9, 37);
			this->label25->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label25->Name = L"label25";
			this->label25->Size = System::Drawing::Size(151, 20);
			this->label25->TabIndex = 8;
			this->label25->Text = L"Custom Menu Index";
			// 
			// customMenuIndex
			// 
			this->customMenuIndex->Location = System::Drawing::Point(332, 31);
			this->customMenuIndex->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->customMenuIndex->Name = L"customMenuIndex";
			this->customMenuIndex->Size = System::Drawing::Size(69, 26);
			this->customMenuIndex->TabIndex = 7;
			this->customMenuIndex->Text = L"8";
			this->customMenuIndex->TextAlign = System::Windows::Forms::HorizontalAlignment::Right;
			// 
			// label24
			// 
			this->label24->AutoSize = true;
			this->label24->Location = System::Drawing::Point(9, 77);
			this->label24->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label24->Name = L"label24";
			this->label24->Size = System::Drawing::Size(133, 20);
			this->label24->TabIndex = 6;
			this->label24->Text = L"UEM Script Index";
			// 
			// loadSettingsButton
			// 
			this->loadSettingsButton->Location = System::Drawing::Point(9, 723);
			this->loadSettingsButton->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->loadSettingsButton->Name = L"loadSettingsButton";
			this->loadSettingsButton->Size = System::Drawing::Size(162, 78);
			this->loadSettingsButton->TabIndex = 14;
			this->loadSettingsButton->Text = L"Reload Settings";
			this->loadSettingsButton->UseVisualStyleBackColor = true;
			this->loadSettingsButton->Click += gcnew System::EventHandler(this, &UEMAuto::loadSettingsButton_Click);
			// 
			// DefaultSettingsRestore
			// 
			this->DefaultSettingsRestore->Location = System::Drawing::Point(9, 811);
			this->DefaultSettingsRestore->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->DefaultSettingsRestore->Name = L"DefaultSettingsRestore";
			this->DefaultSettingsRestore->Size = System::Drawing::Size(162, 78);
			this->DefaultSettingsRestore->TabIndex = 13;
			this->DefaultSettingsRestore->Text = L"Restore Defaults";
			this->DefaultSettingsRestore->UseVisualStyleBackColor = true;
			this->DefaultSettingsRestore->Click += gcnew System::EventHandler(this, &UEMAuto::DefaultSettingsRestore_Click);
			// 
			// SaveSettingsButton
			// 
			this->SaveSettingsButton->Location = System::Drawing::Point(1024, 811);
			this->SaveSettingsButton->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->SaveSettingsButton->Name = L"SaveSettingsButton";
			this->SaveSettingsButton->Size = System::Drawing::Size(148, 78);
			this->SaveSettingsButton->TabIndex = 12;
			this->SaveSettingsButton->Text = L"Save Settings";
			this->SaveSettingsButton->UseVisualStyleBackColor = true;
			this->SaveSettingsButton->Click += gcnew System::EventHandler(this, &UEMAuto::SaveSettingsButton_Click);
			// 
			// GeneralSettingsBox
			// 
			this->GeneralSettingsBox->Controls->Add(this->timeZeroPositionSetting);
			this->GeneralSettingsBox->Controls->Add(this->label16);
			this->GeneralSettingsBox->Location = System::Drawing::Point(22, 112);
			this->GeneralSettingsBox->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->GeneralSettingsBox->Name = L"GeneralSettingsBox";
			this->GeneralSettingsBox->Padding = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->GeneralSettingsBox->Size = System::Drawing::Size(412, 77);
			this->GeneralSettingsBox->TabIndex = 10;
			this->GeneralSettingsBox->TabStop = false;
			this->GeneralSettingsBox->Text = L"General Settings";
			// 
			// timeZeroPositionSetting
			// 
			this->timeZeroPositionSetting->Location = System::Drawing::Point(262, 29);
			this->timeZeroPositionSetting->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->timeZeroPositionSetting->Name = L"timeZeroPositionSetting";
			this->timeZeroPositionSetting->Size = System::Drawing::Size(139, 26);
			this->timeZeroPositionSetting->TabIndex = 7;
			this->timeZeroPositionSetting->Text = L"293.527";
			this->timeZeroPositionSetting->TextAlign = System::Windows::Forms::HorizontalAlignment::Right;
			this->timeZeroPositionSetting->LostFocus += gcnew System::EventHandler(this, &UEMAuto::timeZeroPositionSetting_TextChanged);
			// 
			// label16
			// 
			this->label16->AutoSize = true;
			this->label16->Location = System::Drawing::Point(9, 34);
			this->label16->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label16->Name = L"label16";
			this->label16->Size = System::Drawing::Size(224, 20);
			this->label16->TabIndex = 6;
			this->label16->Text = L"True Time Zero Position (mm): ";
			// 
			// DelaySettingsBox
			// 
			this->DelaySettingsBox->Controls->Add(this->label15);
			this->DelaySettingsBox->Controls->Add(this->delaySpeedSetting);
			this->DelaySettingsBox->Location = System::Drawing::Point(444, 26);
			this->DelaySettingsBox->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->DelaySettingsBox->Name = L"DelaySettingsBox";
			this->DelaySettingsBox->Padding = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->DelaySettingsBox->Size = System::Drawing::Size(207, 77);
			this->DelaySettingsBox->TabIndex = 9;
			this->DelaySettingsBox->TabStop = false;
			this->DelaySettingsBox->Text = L"Delay Stage Settings";
			// 
			// label15
			// 
			this->label15->AutoSize = true;
			this->label15->Location = System::Drawing::Point(9, 34);
			this->label15->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label15->Name = L"label15";
			this->label15->Size = System::Drawing::Size(116, 20);
			this->label15->TabIndex = 5;
			this->label15->Text = L"Default Speed:";
			// 
			// delaySpeedSetting
			// 
			this->delaySpeedSetting->Location = System::Drawing::Point(0, 0);
			this->delaySpeedSetting->Name = L"delaySpeedSetting";
			this->delaySpeedSetting->Size = System::Drawing::Size(100, 26);
			this->delaySpeedSetting->TabIndex = 6;
			// 
			// CameraSettingsBox
			// 
			this->CameraSettingsBox->Controls->Add(this->label5);
			this->CameraSettingsBox->Controls->Add(this->DelayIPSetting);
			this->CameraSettingsBox->Location = System::Drawing::Point(22, 26);
			this->CameraSettingsBox->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->CameraSettingsBox->Name = L"CameraSettingsBox";
			this->CameraSettingsBox->Padding = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->CameraSettingsBox->Size = System::Drawing::Size(412, 77);
			this->CameraSettingsBox->TabIndex = 8;
			this->CameraSettingsBox->TabStop = false;
			this->CameraSettingsBox->Text = L"Camera Settings";
			// 
			// label5
			// 
			this->label5->AutoSize = true;
			this->label5->Location = System::Drawing::Point(9, 34);
			this->label5->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->label5->Name = L"label5";
			this->label5->Size = System::Drawing::Size(197, 20);
			this->label5->TabIndex = 5;
			this->label5->Text = L"Delay Stage Computer IP: ";
			// 
			// DelayIPSetting
			// 
			this->DelayIPSetting->Location = System::Drawing::Point(262, 29);
			this->DelayIPSetting->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->DelayIPSetting->Name = L"DelayIPSetting";
			this->DelayIPSetting->Size = System::Drawing::Size(140, 26);
			this->DelayIPSetting->TabIndex = 4;
			this->DelayIPSetting->Text = L"192.168.0.3";
			this->DelayIPSetting->TextAlign = System::Windows::Forms::HorizontalAlignment::Right;
			this->DelayIPSetting->TextChanged += gcnew System::EventHandler(this, &UEMAuto::DelayIPSetting_TextChanged);
			// 
			// trackTime
			// 
			this->trackTime->WorkerSupportsCancellation = true;
			this->trackTime->DoWork += gcnew System::ComponentModel::DoWorkEventHandler(this, &UEMAuto::timeTracker_DoWork);
			// 
			// curTime
			// 
			this->curTime->AutoSize = true;
			this->curTime->Location = System::Drawing::Point(26, 1026);
			this->curTime->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->curTime->Name = L"curTime";
			this->curTime->Size = System::Drawing::Size(71, 20);
			this->curTime->TabIndex = 2;
			this->curTime->Text = L"00:00:00";
			// 
			// delayComm
			// 
			this->delayComm->WorkerSupportsCancellation = true;
			this->delayComm->DoWork += gcnew System::ComponentModel::DoWorkEventHandler(this, &UEMAuto::DelayComm_DoWork);
			// 
			// scanRunner
			// 
			this->scanRunner->WorkerSupportsCancellation = true;
			this->scanRunner->DoWork += gcnew System::ComponentModel::DoWorkEventHandler(this, &UEMAuto::ScanRunner_DoWork);
			// 
			// cameraRunner
			// 
			this->cameraRunner->WorkerSupportsCancellation = true;
			this->cameraRunner->DoWork += gcnew System::ComponentModel::DoWorkEventHandler(this, &UEMAuto::CameraRunner_DoWork);
			// 
			// delayValueUpdater
			// 
			this->delayValueUpdater->WorkerSupportsCancellation = true;
			this->delayValueUpdater->DoWork += gcnew System::ComponentModel::DoWorkEventHandler(this, &UEMAuto::DelayValueUpdater_DoWork);
			// 
			// versionNumber
			// 
			this->versionNumber->AutoSize = true;
			this->versionNumber->Location = System::Drawing::Point(1122, 14);
			this->versionNumber->Margin = System::Windows::Forms::Padding(4, 0, 4, 0);
			this->versionNumber->Name = L"versionNumber";
			this->versionNumber->Size = System::Drawing::Size(89, 20);
			this->versionNumber->TabIndex = 15;
			this->versionNumber->Text = L"Version 1.5";
			// 
			// UEMAuto
			// 
			this->AutoScaleDimensions = System::Drawing::SizeF(9, 20);
			this->AutoScaleMode = System::Windows::Forms::AutoScaleMode::Font;
			this->ClientSize = System::Drawing::Size(1234, 1060);
			this->Controls->Add(this->versionNumber);
			this->Controls->Add(this->curTime);
			this->Controls->Add(this->cameraTab);
			this->Controls->Add(this->label1);
			this->Icon = (cli::safe_cast<System::Drawing::Icon^>(resources->GetObject(L"$this.Icon")));
			this->Margin = System::Windows::Forms::Padding(4, 5, 4, 5);
			this->Name = L"UEMAuto";
			this->Text = L"UEMtomaton";
			this->cameraTab->ResumeLayout(false);
			this->tabPage2->ResumeLayout(false);
			this->tabPage2->PerformLayout();
			(cli::safe_cast<System::ComponentModel::ISupportInitialize^>(this->DataReadouts))->EndInit();
			(cli::safe_cast<System::ComponentModel::ISupportInitialize^>(this->TimePoints))->EndInit();
			this->delayTab->ResumeLayout(false);
			this->delayTab->PerformLayout();
			this->groupBox1->ResumeLayout(false);
			this->groupBox1->PerformLayout();
			this->tabPage3->ResumeLayout(false);
			this->tabPage3->PerformLayout();
			this->tabPage1->ResumeLayout(false);
			this->groupBox2->ResumeLayout(false);
			this->groupBox2->PerformLayout();
			this->GeneralSettingsBox->ResumeLayout(false);
			this->GeneralSettingsBox->PerformLayout();
			this->DelaySettingsBox->ResumeLayout(false);
			this->DelaySettingsBox->PerformLayout();
			this->CameraSettingsBox->ResumeLayout(false);
			this->CameraSettingsBox->PerformLayout();
			this->ResumeLayout(false);
			this->PerformLayout();

		}
#pragma endregion



		/* ServInitButton_Click
			Function that will initialize the server. Intended for delay-stage side.

			Uses port 6666 for the delay value communication to the camera computer
			Uses port 6667 for the camera run-status communication to the camera computer 
		*/
		private: System::Void ServInitButton_Click(System::Object^ sender, System::EventArgs^ e) 
		{

			// Update the user on beginning initialization
			String^ upStat = gcnew String("Initializing server...\r\n");
			this->statusWindow->AppendText(upStat);

			// standard server startup code --> search Berkeley sockets or c++ sockets for more information
			WSAStartup(MAKEWORD(2, 0), &WSAData);
			dc_server = socket(AF_INET, SOCK_STREAM, 0);
			cc_server = socket(AF_INET, SOCK_STREAM, 0);

			dc_serverAddr.sin_addr.s_addr = INADDR_ANY;
			dc_serverAddr.sin_family = AF_INET;
			dc_serverAddr.sin_port = htons(6666);

			cc_serverAddr.sin_addr.s_addr = INADDR_ANY;
			cc_serverAddr.sin_family = AF_INET;
			cc_serverAddr.sin_port = htons(6667);

			bind(dc_server, (SOCKADDR*)& dc_serverAddr, sizeof(dc_serverAddr));
			listen(dc_server, 0);

			bind(cc_server, (SOCKADDR*)& cc_serverAddr, sizeof(cc_serverAddr));
			listen(cc_server, 0);

			// Update the user on listening for the connection to the delay value client and run client
			upStat = gcnew String("Listening for incoming connections on ports 6666 and 6667...\r\n");
			this->statusWindow->AppendText(upStat);

			dc_clientAddrSize = sizeof(dc_clientAddr);
			cc_clientAddrSize = sizeof(cc_clientAddr);

			// Connect to the delay value client
			if ((delaycomm_client = accept(dc_server, (SOCKADDR*)& dc_clientAddr, &dc_clientAddrSize)) != INVALID_SOCKET)
			{
				upStat = gcnew String("Delay data transferring.\r\n");
				this->statusWindow->AppendText(upStat);
			}

			// Connect to the camera run status client
			if ((camcomm_client = accept(cc_server, (SOCKADDR*)& cc_clientAddr, &cc_clientAddrSize)) != INVALID_SOCKET)
			{
				upStat = gcnew String("Camera data communicating.\r\n");
				this->statusWindow->AppendText(upStat);
			}
			
			if (delayConnected == 0)
			{
				// inject code here to connect the delay stage via IronPython script
				// 
				// Spawns the .exe
				spawnl(P_NOWAIT, "DelayStageCommScript.exe", "DelayStageCommScript.exe", NULL);
				// //!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
				// ipy script will auto-initialize awaiting orders and communicating its position via text files (no better way without coding some stupid socket solution or some other communications protocol between ipy and C++
				delayConnected = 1;

				this->scanRunner->RunWorkerAsync(); // run the scan-thread
				this->delayValueUpdater->RunWorkerAsync();
			}
			else
			{
				this->statusWindow->AppendText("Delay stage already connected.\r\n");
			}

			this->trackTime->RunWorkerAsync();
	
			this->statusWindow->AppendText("Ready for scan.\r\n");

		}

		private: System::Void cleanupSockets()
		{
			closesocket(dc_server);
			closesocket(cc_server);
			WSACleanup();
		}

		/*
		*/
		static BOOL CALLBACK FindTheDesiredWnd(HWND hWnd, LPARAM lParam)
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
		/* RunScan_Click
			Begins a scan containing the experimental time point array. Sends a signal to the camera computer that a scan has begun as well.
		*/
		private: System::Void RunScan_Click(System::Object^ sender, System::EventArgs^ e) 
		{
			HWND hFoundWnd = NULL;
			WindowSearcher finder;
			hFoundWnd = finder.FocusWindow();
			if (hFoundWnd != NULL)
			{
				// move to foreground
				this->WindowState = System::Windows::Forms::FormWindowState::Minimized;
				this->WindowState = System::Windows::Forms::FormWindowState::Normal; // this is the dumbest hack I've tried and I'm almost ashamed it works. Almost.
				//SetWindowPos(hWnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE);
				SetForegroundWindowInternal(hFoundWnd);
				//SetActiveWindow(hWnd);
				// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! RUNUEMSCAN AHK
				spawnl(P_NOWAIT, "UEMtomatonCameraAcquisition.exe", "UEMtomatonCameraAcquisition.exe", NULL);

				System::Threading::Thread::Sleep(30);

				this->WindowState = System::Windows::Forms::FormWindowState::Minimized;
				this->WindowState = System::Windows::Forms::FormWindowState::Normal; // facepalm
			}
			else
			{
				String^ upStat = gcnew String("Window containing DigitalMicrograph title was not found.\r\n");
				this->camStat->AppendText(upStat);
			}

			runStat = 1; // set state of run to running

			this->pauseButton->ForeColor.Black; // set the pause button to black
			this->pauseButton->Refresh();
			this->playRun->ForeColor.AliceBlue; // set the play button to blue
			this->playRun->Refresh();
			this->cameraRunner->RunWorkerAsync();

		}
		 
		/* MakeTimeButton_Click
			Opens the MakeTimepoints.exe program and loads the results into the main program. Uses that data to make the timepoint table, timepoint array, and experimental array.
		*/
		private: System::Void MakeTimeButton_Click(System::Object^ sender, System::EventArgs^ e)
		{

			// Update the user on making timepoints sub-program.
			String^ upStat = gcnew String("Started MakeTimepoints.exe.\r\n");
			this->statusWindow->AppendText(upStat);

			// Spawns the .exe
			spawnl(P_WAIT, "MakeTimepoints.exe", "MakeTimepoints.exe", NULL);

			// Grabs the time points from the program.
			upStat = gcnew String("Grabbing timepoints.\r\n");
			this->statusWindow->AppendText(upStat);

			std::ifstream OpenFile;
			double startIn, endIn, sepIn;
			int pointIn;

			int curRow = 0;
			int lastQu, throwaway1, throwaway2;
			int numLines = 0;
			totPoints = 0;
			std::string line;

			OpenFile.open("TimeInputs.txt");

			do
			{

				getline(OpenFile, line);
				numLines++;

			} while (!OpenFile.eof());

			const int numRows = numLines-2;

			timeTable = new double[4*numRows];

			OpenFile.clear();
			OpenFile.seekg(0, std::ios::beg);

			// Begin assembling the timetable

			getline(OpenFile, line);

			std::istringstream ss(line);

			ss >> lastQu >> throwaway1 >> throwaway2;
			includeLast = lastQu;

			while (getline(OpenFile, line))
			{
				std::istringstream ss(line);

				ss >> startIn >> endIn >> sepIn;

				pointIn = (int)floor(abs(endIn-startIn)/sepIn);

				timeTable[curRow*4] = startIn;
				timeTable[curRow*4+1] = endIn;
				timeTable[curRow*4+2] = sepIn;
				timeTable[curRow*4+3] = pointIn;

				totPoints = totPoints + pointIn;

				curRow++;
			}

			OpenFile.close();

			if (includeLast == 1)
			{
				totPoints++;
			}

			const int tpV = totPoints;

			// Begin assembling the time point array

			timeptArr = new double[tpV];
			int curLinePt = 0;

			for (int a = 0; a < numRows; a++)
			{
				for (int b = 0; b < timeTable[a*4+3]; b++)
				{
					timeptArr[curLinePt + b] = timeTable[a*4] + timeTable[a*4+2] * b;
				}
				curLinePt = curLinePt + timeTable[a*4+3];
			}

			if (includeLast == 1)
			{
				timeptArr[tpV - 1] = timeTable[(numRows - 1)*4 + 1];
			}

			// Begin assembling the experimental array
			expArr = new double[tpV];

			for (int a = 0; a < tpV; a++)
			{
				expArr[a] = timeptArr[a];
			}

			this->TimePoints->Rows->Clear();
			this->TimePoints->Refresh();

			if (randomized == 1)
			{
				std::random_shuffle(&expArr[0], &expArr[tpV]);

				for (int a = 0; a < tpV; a++)
				{
					String^ timeAdd = gcnew String(std::to_string(expArr[a]).c_str());
				
					this->TimePoints->Rows->Add(timeAdd);
				}
			}
			else
			{
				for (int a = 0; a < tpV; a++)
				{
					String^ timeAdd = gcnew String(std::to_string(expArr[a]).c_str());

					this->TimePoints->Rows->Add(timeAdd);
				}
			}

		}

		/* RandomPoints_CheckedChanged
			Checks if the timepoints should be randomized or not. Adjusts the time array accordingly.
		*/

		private: System::Void RandomPoints_CheckedChanged(System::Object^ sender, System::EventArgs^ e) 
		{

			const int tpV = totPoints;
			expArr = new double[tpV];

			this->TimePoints->Rows->Clear();
			this->TimePoints->Refresh();

			for (int a = 0; a < tpV; a++)
			{
				expArr[a] = timeptArr[a];
			}

			if (this->randomPoints->Checked)
			{
				randomized = 1;

				unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
				std::shuffle(&expArr[0], &expArr[tpV], std::default_random_engine(seed));

				for (int a = 0; a < tpV; a++)
				{
					String^ timeAdd = gcnew String(std::to_string(expArr[a]).c_str());

					this->TimePoints->Rows->Add(timeAdd);
				}

				String^ upStat = gcnew String("Randomized timepoints.\r\n");
				this->statusWindow->AppendText(upStat);

			}
			else
			{
				randomized = 0;

				for (int a = 0; a < tpV; a++)
				{
					String^ timeAdd = gcnew String(std::to_string(expArr[a]).c_str());

					this->TimePoints->Rows->Add(timeAdd);
				}

				String^ upStat = gcnew String("Unrandomized timepoints.\r\n");
				this->statusWindow->AppendText(upStat);
			}

		}

		/* DisconServ_Click
			Close all sockets and execute WSACleanup. Cancel the delay-value communication thread.
		*/
		private: System::Void DisconServ_Click(System::Object^ sender, System::EventArgs^ e)
		{
	
			closesocket(delaycomm_client);
			closesocket(camcomm_client);

			WSACleanup();

			// initialize a full disconnect in ironpython
			//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
			// Requires setting connect text file to "2"
			std::ofstream OpenFile;

			OpenFile.open("connectStatFile.txt");

			OpenFile << "2";

			OpenFile.close();

			delayConnected = 0;

			String^ upStat = gcnew String("Server shutdown.\r\n");
			this->statusWindow->AppendText(upStat);

			this->trackTime->CancelAsync();
	
		}

		/* timeTracker_DoWork and associated delegate functions. Intended for delay-stage computer.
			Named as such because it tracks the amount of time delay data has been passing between the two computers, but also passes the delay values.

			UpdateTime-TimeUpdater delegate pair: Used to update the time in the bottom left corner.
			delStopComm-stopDelComm delegate pair: Used to cancel timeTracker_DoWork in the event of a disconnect from the delay stage.
		*/
		delegate System::Void UpdateTime(String^ TimeUp);
		System::Void TimeUpdater(String^ TimeUp) 
		{
			this->curTime->Text = TimeUp;
			this->curTime->Update();
		}
		delegate System::Void delStopComm();
		System::Void stopDelComm()
		{
			this->delayComm->CancelAsync();
		}
		delegate System::Void timeStopTrack();
		System::Void stopTrackTime()
		{
			this->trackTime->CancelAsync();
		}
		delegate System::Void delPosDisUp(double curPos);
		private: System::Void timeTracker_DoWork(System::Object^ sender, System::ComponentModel::DoWorkEventArgs^ e)
		{

			System::Threading::Thread::Sleep(1000);

			// ADD DELAY VALUE PASSING
			int connectHealth;
			DateTime initTime = DateTime::Now;
			DateTime curTime;
			TimeSpan connectTime;
			int cumulTime;
			std::string conTime;
			int a;
			std::string curdelPosStr;
			std::string curdelTimStr;

			while (true)
			{

				System::Threading::Thread::Sleep(100);

				curTime = DateTime::Now;
				connectTime = curTime - initTime;
				my_time = time(NULL);
				cumulTime = (int)round((double)connectTime.TotalSeconds);

				conTime = std::to_string(cumulTime);

				dc_buffer[0] = '0';

				for (a = 1; a < conTime.length() + 1; a++)
				{
					dc_buffer[a] = (char)conTime[a - 1];

					if (a == conTime.length() + 1)
					{
						dc_buffer[a + 1] = '|';
						dc_buffer[a + 2] = '\0';
					}
				}

				connectHealth = send(delaycomm_client, dc_buffer, sizeof(dc_buffer), 0);

				if (connectHealth == SOCKET_ERROR)
				{
					cleanupSockets();
					cleanupDelay();
					this->BeginInvoke(gcnew timeStopTrack(this, &UEMAuto::stopTrackTime));
				}

				memset(dc_buffer, 0, sizeof(dc_buffer));

				this->BeginInvoke(gcnew UpdateTime(this, &UEMAuto::TimeUpdater), gcnew String(ctime(&my_time)));

				curdelPosStr = msclr::interop::marshal_as<std::string>(this->delayPosDist->Text);
				curdelTimStr = msclr::interop::marshal_as<std::string>(this->delayPosTime->Text);

				dc_buffer[0] = '1';

				for (a = 1; a < curdelPosStr.length() + 1; a++)
				{
					dc_buffer[a] = curdelPosStr[a - 1];
				}
				dc_buffer[curdelPosStr.length() + 1] = '|';
				for (a = curdelPosStr.length() + 2; a < curdelPosStr.length() + curdelTimStr.length() + 2; a++)
				{
					dc_buffer[a] = curdelTimStr[a - curdelPosStr.length() - 2];
				}
				dc_buffer[curdelPosStr.length() + curdelTimStr.length() + 2] = '|';
				dc_buffer[curdelPosStr.length() + curdelTimStr.length() + 3] = '\0';

				connectHealth = send(delaycomm_client, dc_buffer, sizeof(dc_buffer), 0);

				if (connectHealth == SOCKET_ERROR)
				{
					cleanupSockets();
					cleanupDelay();
					this->BeginInvoke(gcnew timeStopTrack(this, &UEMAuto::stopTrackTime));
				}

				memset(dc_buffer, 0, sizeof(dc_buffer));

			}

			this->BeginInvoke(gcnew delStopComm(this, &UEMAuto::stopDelComm));
			this->BeginInvoke(gcnew timeStopTrack(this, &UEMAuto::stopTrackTime));

		}

		/* DelayComm_DoWork and associated delegate functions. Intended for camera computer
			Will receive the amount of time connected as well as the delay stage readouts.

			Borrows timeTracker_DoWork's delegate UpdateTime-TimeUpdater.
		*/
		delegate System::Void camPosDisUp(String^ curPos);
		System::Void camDisPosUp(String^ curPos)
		{
			this->camDelPosMM->Text = curPos;
		}
		delegate System::Void camPosTimUp(String^ curTim);
		System::Void camDisTimUp(String^ curTim)
		{
			this->camDelPosPS->Text = curTim;
		}
		private: System::Void DelayComm_DoWork(System::Object^ sender, System::ComponentModel::DoWorkEventArgs^ e) 
		{
			int connectHealth;
			char curChar;
			int sizeData;
			int tracker = 0;
			char* data;
			int sizeDelayPos;
			int sizeDelayTime;
			char* posdata;
			char* timdata;
			int a;

			do
			{
				connectHealth = recv(dc_server, dc_buffer, sizeof(dc_buffer), 0);

				if (connectHealth == SOCKET_ERROR)
				{
					cleanupSockets();
					cleanupDelay();
					this->BeginInvoke(gcnew delStopComm(this, &UEMAuto::stopDelComm));
				}

				if (dc_buffer[0] == '0')
				{
					curChar = dc_buffer[1];
					sizeData = 0;
					tracker = 1;

					while (curChar != '|')
					{
						sizeData++;
						tracker++;
						curChar = dc_buffer[tracker];
					}

					data = new char[sizeData + 1];

					for (a = 1; a < sizeData + 1; a++)
					{
						data[a - 1] = dc_buffer[a];
					}

					data[sizeData] = '\0';

					this->BeginInvoke(gcnew UpdateTime(this, &UEMAuto::TimeUpdater), gcnew String(data));
				}
				else if (dc_buffer[0] == '1')
				{
					curChar = dc_buffer[1];
					sizeDelayPos = 0;
					sizeDelayTime = 0;
					tracker = 1;

					while (curChar != '|')
					{
						sizeDelayPos++;
						tracker++;
						curChar = dc_buffer[tracker];
					}

					tracker++;
					curChar = dc_buffer[tracker];

					while (curChar != '|')
					{
						sizeDelayTime++;
						tracker++;
						curChar = dc_buffer[tracker];
					}

					posdata = new char[sizeDelayPos + 1];
					timdata = new char[sizeDelayTime + 1];

					for (a = 1; a < sizeDelayPos + 1; a++)
					{
						posdata[a - 1] = dc_buffer[a];
					}

					for (a = sizeDelayPos + 2; a < sizeDelayPos + sizeDelayTime + 2; a++)
					{
						timdata[a - sizeDelayPos - 2] = dc_buffer[a];
					}

					posdata[sizeDelayPos] = '\0';
					timdata[sizeDelayTime] = '\0';

					this->BeginInvoke(gcnew camPosDisUp(this, &UEMAuto::camDisPosUp), gcnew String(posdata));
					this->BeginInvoke(gcnew camPosTimUp(this, &UEMAuto::camDisTimUp), gcnew String(timdata));
				}

				memset(dc_buffer, 0, sizeof(dc_buffer));

			} while (true);

		}

		/* ServConnButton_Click
			Connects the camera computer to the delay stage server and initiates two background threads
		*/
		private: System::Void ServConnButton_Click(System::Object^ sender, System::EventArgs^ e) 
		{

			int sock1Res;
			int sock2Res;
			String^ upStat;

			WSAStartup(MAKEWORD(2, 0), &WSAData);
			dc_server = socket(AF_INET, SOCK_STREAM, 0);
			cc_server = socket(AF_INET, SOCK_STREAM, 0);

			inet_pton(AF_INET, msclr::interop::marshal_as<std::string>(this->servIP->Text).c_str(), &dc_addr.sin_addr.s_addr);
			dc_addr.sin_family = AF_INET;
			dc_addr.sin_port = htons(6666);

			inet_pton(AF_INET, msclr::interop::marshal_as<std::string>(this->servIP->Text).c_str(), &cc_addr.sin_addr.s_addr);
			cc_addr.sin_family = AF_INET;
			cc_addr.sin_port = htons(6667);

			upStat = gcnew String("Searching for connection. Blocking rest of program until connection established.\r\n");
			this->camStat->AppendText(upStat);

			servAddrSize = sizeof(dc_addr);
			sock1Res = connect(dc_server, (SOCKADDR*)& dc_addr, sizeof(dc_addr));

			servAddrSize = sizeof(cc_addr);
			sock2Res = connect(cc_server, (SOCKADDR*)&cc_addr, sizeof(cc_addr));

			if (sock1Res == SOCKET_ERROR || sock2Res == SOCKET_ERROR)
			{
				upStat = gcnew String("connect function failed with error:" + WSAGetLastError() + "\r\n");
				this->camStat->AppendText(upStat);

				sock1Res = closesocket(dc_server);
				if (sock1Res == SOCKET_ERROR)
				{
					upStat = gcnew String("closesocket function failed with error:" + WSAGetLastError() + "\r\n");
					this->camStat->AppendText(upStat);
				}

				upStat = gcnew String("connect function failed with error:" + WSAGetLastError() + "\r\n");
				this->camStat->AppendText(upStat);

				sock2Res = closesocket(cc_server);
				if (sock2Res == SOCKET_ERROR)
				{
					upStat = gcnew String("closesocket function failed with error:" + WSAGetLastError() + "\r\n");
					this->camStat->AppendText(upStat);
				}

				WSACleanup();
			}
			else
			{
				upStat = gcnew String("Connected to server!\r\n");
				this->camStat->AppendText(upStat);

				this->delayComm->RunWorkerAsync();
			}

		}

		/* DisconCam_Click
			Disconnects the camera computer from the delay stage and stops the background threads
		*/
		private: System::Void DisconCam_Click(System::Object^ sender, System::EventArgs^ e) 
		{
	
			closesocket(dc_server);
			closesocket(cc_server);
			WSACleanup();
			String^ upStat = gcnew String("Socket closed.\r\n");
			this->camStat->AppendText(upStat);
			this->cameraRunner->CancelAsync();
			this->delayComm->CancelAsync();

		}

		/* CameraRunner_DoWork and associated delegate functions. Intended for the camera computer.
			This function is the one that handles all initiated scans.

			AddDelRunGridRow-DelGridRowAdd delegate pair: Updates the run log with the current step
			DelRunGridRowUp-DelGridRowUp delegate pair: Updates the status of the current step
			DelRunGridClear-DelGridRunClear delegate pair: Clears the log
			delStopRun-stopDelRun delegate pair: Stops the main method
			upDelRunProg-upDelProgRun delegate pair: Updates the progress bar for the run
			upEstTime-upTimeEst delegate pair: Updates the estimated time for the scan to run
			SetForegroundWindowInternal: function intended to set DM to the foreground
			PressKey: Presses a key in the computer.
			PressEnter: Presses the enter key in the computer.
		*/
		delegate System::Void AddDelRunGridRow(String^ step, String^ TimePoint, String^ DelPos, String^ status);
		System::Void DelGridRowAdd(String^ step, String^ TimePoint, String^ DelPos, String^ status)
		{
			this->DataReadouts->Rows->Add(step, TimePoint, DelPos, status);
		}
		delegate System::Void DelRunGridRowUp(String^ status);
		System::Void DelGridRowUp(String^ status)
		{
			this->DataReadouts->Rows[this->DataReadouts->RowCount - 1]->Cells[3]->Value = status;
		}
		delegate System::Void DelRunGridClear();
		System::Void DelGridRunClear()
		{
			this->DataReadouts->Rows->Clear();
			this->DataReadouts->Update();
		}
		delegate System::Void delStopRun();
		System::Void stopDelRun()
		{
			this->scanRunner->CancelAsync();
		}
		delegate System::Void upDelRunProg(int stepVal);
		System::Void upDelProgRun(int stepVal)
		{
			this->runProg->Minimum = 0;
			this->runProg->Maximum = totPoints * (repeatValue + 1);
			this->runProg->Value = stepVal + 1;
			this->runProg->Update();
		}
		delegate System::Void upEstTime(double timePer, int curStep);
		System::Void upTimeEst(double timePer, int curStep)
		{
			timeLeft = round(timePer * (totPoints*(repeatValue+1) - curStep));
			/*
			String^ upStat = gcnew String(curStep.ToString() + "\r\n");
			this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);
			upStat = gcnew String(repeatValue.ToString() + "\r\n");
			this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);
			upStat = gcnew String(totPoints.ToString() + "\r\n");
			this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);
			upStat = gcnew String(timePer.ToString() + "\r\n");
			this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);
			*/
			this->timeRemLab->Text = gcnew String(std::to_string((int)timeLeft).c_str()) + " sec";
		}
		delegate System::Void progIndicatorReset();
		System::Void resetProgIndicators()
		{
			this->timeRemLab->Text = "Complete";
			this->runProg->Minimum = 0;
			this->runProg->Maximum = 1;
			this->runProg->Value = 0;
			this->runProg->Update();
		}
		void SetForegroundWindowInternal(HWND hWnd)
		{
			if (!::IsWindow(hWnd)) return;

			BYTE keyState[256] = { 0 };
			//to unlock SetForegroundWindow we need to imitate Alt pressing
			if (::GetKeyboardState((LPBYTE)& keyState))
			{
				if (!(keyState[VK_MENU] & 0x80))
				{
					::keybd_event(VK_MENU, 0, KEYEVENTF_EXTENDEDKEY | 0, 0);
				}
			}

			::SetForegroundWindow(hWnd);

			if (::GetKeyboardState((LPBYTE)& keyState))
			{
				if (!(keyState[VK_MENU] & 0x80))
				{
					::keybd_event(VK_MENU, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0);
				}
			}
		}
		void PressKey(WORD keypress)
		{
			INPUT input;
			WORD vkey = keypress; // see link below
			input.type = INPUT_KEYBOARD;
			input.ki.wScan = MapVirtualKey(vkey, MAPVK_VK_TO_VSC);
			input.ki.time = 0;
			input.ki.dwExtraInfo = 0;
			input.ki.wVk = vkey;
			input.ki.dwFlags = 0; // there is no KEYEVENTF_KEYDOWN
			SendInput(1, &input, sizeof(INPUT));

			System::Threading::Thread::Sleep(30);
			input.ki.dwFlags = KEYEVENTF_KEYUP;
			SendInput(1, &input, sizeof(INPUT));
		}
		void PressEnter()
		{
			INPUT ip;
			ip.type = INPUT_KEYBOARD;
			ip.ki.time = 0;
			ip.ki.dwFlags = KEYEVENTF_UNICODE;
			ip.ki.wScan = VK_RETURN; //VK_RETURN is the code of Return key
			ip.ki.wVk = 0;

			ip.ki.dwExtraInfo = 0;
			SendInput(1, &ip, sizeof(INPUT));

		}
		delegate System::Void UpdateCamStatus(String^ appStat);
		System::Void CamStatUpdater(String^ appStat)
		{
			this->camStat->AppendText(appStat);
		}
		delegate System::Void cameraRunnerStop();
		System::Void stopCameraRunner()
		{
			this->cameraRunner->CancelAsync();
		}
		private: System::Void CameraRunner_DoWork(System::Object^ sender, System::ComponentModel::DoWorkEventArgs^ e) 
		{

			int connectHealth = 0;
			int firstPass = 0;
			int recvSignal = 0;
			int firstPause = 1;
			int curStep = 0; // current step in the entire image set, including repeats
			int curScan = 0; // current scan
			int curScanStep = 0; /// current step in the scan, not including previous scans
			int a;

			DateTime timeInit;
			DateTime timeTrack;

			TimeSpan addTime;
			TimeSpan cumulTime;
			double timeSpent;
			double timePer;
			double curTimePoint;
			double curDistPoint;

			String^ upStat;
			String^ stepString;
			String^ timeString;
			String^ posString;
			String^ statString;

			//struct stat buffer;

			FILE* filechecker;
			int fileFound;

			double curDelay = 0;
			WriteULG ulgWriter;
			WriteDMComm dmCommWriter;
			String^ curFileName;
			String^ curFileTot;
			String^ ulgFileName;
			String^ delayText;
			int toCounter = 0;

			std::string timeVal;

			int timeout = 3600 * 4;
			int totImages = totPoints * (repeatValue + 1); // The total number of images including the number of times the scan is to be repeated.

			this->BeginInvoke(gcnew DelRunGridClear(this, &UEMAuto::DelGridRunClear));

			do
			{

				if (WSAGetLastError() == 10054)
				{
					upStat = gcnew String("Network error.\r\n");

					this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);

					runStat = 3;
				}

				butPressMeantime = 0;

				if (runStat == 1)
				{

					timeInit = DateTime::Now;

					if (firstPause == 0)
					{
						firstPause = 1;

						upStat = "Resumed on step " + gcnew String(std::to_string(curStep + 1).c_str()) + ".\r\n";
						this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);
					}

					if (totPoints <= 0 || totPoints.Equals(NULL))
						runStat = 3;
					else
					{

						curTimePoint = expArr[curScanStep];
						curDistPoint = curTimePoint / mm_to_ps + curZero;

						stepString = gcnew String(std::to_string(curScanStep + 1).c_str());
						timeString = gcnew String(std::to_string(curTimePoint).c_str());
						posString = gcnew String(std::to_string(curDistPoint).c_str());
						statString = "Moving delay stage...\r\n";

						this->BeginInvoke(gcnew AddDelRunGridRow(this, &UEMAuto::DelGridRowAdd), stepString, timeString, posString, statString);

						timeVal = std::to_string(expArr[curScanStep]);

						cc_buffer[0] = '1';

						for (a = 1; a <= timeVal.length(); a++)
						{
							cc_buffer[a] = timeVal[a - 1];
						}

						cc_buffer[timeVal.length() + 1] = '|';
						cc_buffer[timeVal.length() + 2] = '\0';

						connectHealth = send(cc_server, cc_buffer, sizeof(cc_buffer), 0);

						if (connectHealth == SOCKET_ERROR)
						{
							cleanupSockets();
							cleanupDelay();
							this->BeginInvoke(gcnew cameraRunnerStop(this, &UEMAuto::stopCameraRunner));
						}

						memset(cc_buffer, 0, sizeof(cc_buffer));

						connectHealth = recv(cc_server, cc_buffer, sizeof(cc_buffer), 0);

						if (connectHealth == SOCKET_ERROR)
						{
							cleanupSockets();
							cleanupDelay();
							this->BeginInvoke(gcnew cameraRunnerStop(this, &UEMAuto::stopCameraRunner));
						}
						
						memset(cc_buffer, 0, sizeof(cc_buffer));
						
						statString = "Acquiring...\r\n";
						this->BeginInvoke(gcnew DelRunGridRowUp(this, &UEMAuto::DelGridRowUp), statString);

						recvSignal = 0;

						if (butPressMeantime == 0)
						{
							runStat = 4;
						}
					}

					timeTrack = DateTime::Now;

					addTime = timeTrack - timeInit;
					cumulTime = cumulTime.Add(addTime);

				}
				else if (runStat == 2)
				{
					// Pause signal, to wait for resume button. Allows current step to complete. Blocking only occurs once here.
					if (recvSignal == 0)
					{

						timeInit = DateTime::Now;

						// ADJUST FOR DECIMAL DELAYS, WITH LIMITER TO A SINGLE DECIMAL PLACE
						curDelay = curTimePoint;
						if (fmod(curDelay, 1) != 0)
						{
							curDelay = round(curDelay * 10);
							delayText = gcnew String(std::to_string((int)curDelay).c_str()) + "x10";
						}
						else
						{
							delayText = gcnew String(std::to_string((int)curDelay).c_str());
						}

						curFileName = this->fileNameBase->Text + "_" + gcnew String(std::to_string(curScan).c_str()) + "_" + gcnew String(std::to_string(curScanStep + 1).c_str()) + "_" + delayText + gcnew String(units) + ".dm4";
						curFileTot = this->fileSavePath->Text + "\\" + curFileName;
						ulgFileName = this->fileNameBase->Text + ".ulg";

						upStat = "Updating DM communication for step " + gcnew String(std::to_string(curStep + 1).c_str()) + ".\r\n";
						this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);
						// UPDATE CAMERA COMMUNICATION DOCUMENT
						dmCommWriter.WriteData("InputFileTest.txt", msclr::interop::marshal_as<std::string>(this->fileSavePath->Text), msclr::interop::marshal_as<std::string>(this->fileNameBase->Text), std::string(units), std::to_string(curScanStep + 1), msclr::interop::marshal_as<std::string>(delayText), std::to_string(curScan), msclr::interop::marshal_as<std::string>(this->acqTimeBox->Text));

						upStat = "Updating ULG file for step " + gcnew String(std::to_string(curStep + 1).c_str()) + ".\r\n";
						this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);

						// UPDATE ULG
						ulgWriter.WriteData(msclr::interop::marshal_as<std::string>(ulgFileName), msclr::interop::marshal_as<std::string>(this->fileSavePath->Text), msclr::interop::marshal_as<std::string>(this->fileNameBase->Text), std::to_string(totPoints), std::to_string(curStep + 1), std::to_string(curDelay), std::to_string(curScan), std::to_string(curScanStep + 1),  msclr::interop::marshal_as<std::string>(curFileName), curStep + 1);

						upStat = "Waiting to see image name " + curFileTot + " for step " + gcnew String(std::to_string(curStep + 1).c_str()) + ".\r\n";
						this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);

						fileFound = 0;
						// WAITING FOR FILE TO APPEAR. WILL TIME OUT AFTER AN HOUR OF WAITING
						while (fileFound == 0 && toCounter < timeout) // as of August 14th, 2019 this is still experimental
						{
							if (filechecker = fopen(msclr::interop::marshal_as<std::string>(curFileTot).c_str(), "r"))
							{
								fclose(filechecker);
								fileFound = 1;
							}

							toCounter++;
							System::Threading::Thread::Sleep(250);
						}

						if (toCounter < timeout)
							this->BeginInvoke(gcnew DelRunGridRowUp(this, &UEMAuto::DelGridRowUp), "Acquired.");
						else
							this->BeginInvoke(gcnew DelRunGridRowUp(this, &UEMAuto::DelGridRowUp), "Timed out.");

						toCounter = 0;

						recvSignal = 1;

						this->BeginInvoke(gcnew upDelRunProg(this, &UEMAuto::upDelProgRun), curStep);

						curStep++;

						curScanStep = curStep % totPoints; // current step in the scan

						if ((curStep + 1) > totPoints)
						{
							curScan = (curStep - curScanStep) / totPoints; // declares the current scan number (begins at zero and increments upwards)
						}

						timeTrack = DateTime::Now;

						addTime = timeTrack - timeInit;
						cumulTime = cumulTime.Add(addTime);

						timeSpent = cumulTime.TotalSeconds;
						timePer = timeSpent / (curStep + 1);

						this->BeginInvoke(gcnew upEstTime(this, &UEMAuto::upTimeEst), timePer, curStep);
					}
					else
					{
						if (firstPause == 1)
						{
							upStat = "Paused on step " + gcnew String(std::to_string(curStep + 1).c_str()) + ".\r\n";
							this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);
							firstPause = 0;
						}
					}

				}
				else if (runStat == 3)
				{
					// Stop signal, stops and clears everything.

					upStat = "Stopped on step " + gcnew String(std::to_string(curStep + 1).c_str()) + ".\r\n";

					curStep = totPoints;

					this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);
				}
				else if (runStat == 4)
				{

					timeInit = DateTime::Now;
					System::Threading::Thread::Sleep(50);
					// write all the camera communication files and wait for acquisition before moving on
					
					// ADJUST FOR DECIMAL DELAYS, WITH LIMITER TO A SINGLE DECIMAL PLACE
					curDelay = curTimePoint;
					if (fmod(curDelay, 1) != 0)
					{
						curDelay = round(curDelay * 10);
						delayText = gcnew String(std::to_string((int)curDelay).c_str()) + "x10";
					}
					else
					{
						delayText = gcnew String(std::to_string((int)curDelay).c_str());
					}

					/*
					upStat = gcnew String(std::to_string(curDelay).c_str()) + "\r\n\0";

					this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);

					upStat = gcnew String(std::to_string(totPoints).c_str()) + "\r\n\0";

					this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);

					upStat = gcnew String(std::to_string(totImages).c_str()) + "\r\n\0";

					this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);

					upStat = gcnew String(std::to_string(curStep).c_str()) + "\r\n\0";

					this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);

					upStat = gcnew String(std::to_string(curScanStep).c_str()) + "\r\n\0";

					this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);
					*/

					curFileName = this->fileNameBase->Text + "_" + gcnew String(std::to_string(curScan).c_str()) + "_" + gcnew String(std::to_string(curScanStep + 1).c_str()) + "_" + delayText + gcnew String(units) + ".dm4";
					curFileTot = this->fileSavePath->Text + "\\" + curFileName;
					ulgFileName = this->fileSavePath->Text + "\\" + this->fileNameBase->Text + ".ulg";
					
					upStat = "Updating DM communication for step " + gcnew String(std::to_string(curStep + 1).c_str()) + ".\r\n";
					this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);
					// UPDATE CAMERA COMMUNICATION DOCUMENT
					dmCommWriter.WriteData("InputFileTest.txt", msclr::interop::marshal_as<std::string>(this->fileSavePath->Text), msclr::interop::marshal_as<std::string>(this->fileNameBase->Text), std::string(units), std::to_string(curScanStep + 1), msclr::interop::marshal_as<std::string>(delayText), std::to_string(curScan), msclr::interop::marshal_as<std::string>(this->acqTimeBox->Text));

					upStat = "Updating ULG file for step " + gcnew String(std::to_string(curStep + 1).c_str()) + ".\r\n";
					this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);

					// UPDATE ULG
					ulgWriter.WriteData(msclr::interop::marshal_as<std::string>(ulgFileName), msclr::interop::marshal_as<std::string>(this->fileSavePath->Text), msclr::interop::marshal_as<std::string>(this->fileNameBase->Text), std::to_string(totPoints), std::to_string(curStep + 1), std::to_string(curDelay), std::to_string(curScan), std::to_string(curScanStep + 1), msclr::interop::marshal_as<std::string>(curFileName), curStep + 1);

					upStat = "Waiting to see image name " + curFileTot + " for step " + gcnew String(std::to_string(curStep + 1).c_str()) + ".\r\n";
					this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);

					fileFound = 0;
					// WAITING FOR FILE TO APPEAR. WILL TIME OUT AFTER AN HOUR OF WAITING
					while (fileFound == 0 && toCounter < timeout) // as of August 14th, 2019 this is still experimental
					{
						if (filechecker = fopen(msclr::interop::marshal_as<std::string>(curFileTot).c_str(), "r"))
						{
							fclose(filechecker);
							fileFound = 1;
						}

						toCounter++;
						System::Threading::Thread::Sleep(250);
					}

					if (toCounter < timeout)
						this->BeginInvoke(gcnew DelRunGridRowUp(this, &UEMAuto::DelGridRowUp), "Acquired.");
					else
						this->BeginInvoke(gcnew DelRunGridRowUp(this, &UEMAuto::DelGridRowUp), "Timed out.");

					toCounter = 0;

					recvSignal = 1;

					if (butPressMeantime == 0)
					{
						runStat = 1;
					}

					this->BeginInvoke(gcnew upDelRunProg(this, &UEMAuto::upDelProgRun), curStep);

					curStep++;

					curScanStep = curStep % totPoints; // current step in the scan

					if ((curStep + 1) > totPoints)
					{
						curScan = (curStep - curScanStep) / totPoints; // declares the current scan number (begins at zero and increments upwards)
					}

					timeTrack = DateTime::Now;

					addTime = timeTrack - timeInit;
					cumulTime = cumulTime.Add(addTime);

					timeSpent = cumulTime.TotalSeconds;
					timePer = timeSpent / (curStep + 1);

					this->BeginInvoke(gcnew upEstTime(this, &UEMAuto::upTimeEst), timePer, curStep);
				}

				memset(cc_buffer, 0, sizeof(cc_buffer));

			} while (curStep < totImages);

			cc_buffer[0] = '0';
			cc_buffer[1] = '\0';

			connectHealth = send(cc_server, cc_buffer, sizeof(cc_buffer), 0);

			if (connectHealth == SOCKET_ERROR)
			{
				cleanupSockets();
				cleanupDelay();
				this->BeginInvoke(gcnew cameraRunnerStop(this, &UEMAuto::stopCameraRunner));
			}

			memset(cc_buffer, 0, sizeof(cc_buffer));

			upStat = "Scan complete.\r\n";
			this->BeginInvoke(gcnew UpdateCamStatus(this, &UEMAuto::CamStatUpdater), upStat);

			this->BeginInvoke(gcnew progIndicatorReset(this, &UEMAuto::resetProgIndicators));
			this->BeginInvoke(gcnew delStopRun(this, &UEMAuto::stopDelRun));

		}

		/* ScanRunner_DoWork and associated delegate functions
			Handles all the work for organizing the individual steps in a run.

			UpdateDelStatus-DelStatUpdater delegate pair: Updates the status in the bar below
		*/
		delegate System::Void UpdateDelStatus(String^ appStat);
		System::Void DelStatUpdater(String^ appStat)
		{
			this->statusWindow->AppendText(appStat);
		}
		delegate System::Void scanRunStop();
		System::Void stopScanRun()
		{
			this->scanRunner->CancelAsync();
		}
		private: System::Void ScanRunner_DoWork(System::Object^ sender, System::ComponentModel::DoWorkEventArgs^ e) 
		{

			int rundel = 0;
			int connectHealth;

			char curChar;
			int sizeDelayData;
			int tracker = 0;
			char* delaydata;
			int a;
			double curDistPoint;
			std::ifstream OpenFile;
			std::string line;
			std::string completionStatus;
			int completionValue;
			int curLine = 0;

			while (true)
			{

				tracker = 0;

				this->BeginInvoke(gcnew UpdateDelStatus(this, &UEMAuto::DelStatUpdater), gcnew String("Awaiting incoming data.\n"));
				connectHealth = recv(camcomm_client, cc_buffer, sizeof(cc_buffer), 0);

				if (connectHealth == SOCKET_ERROR)
				{
					cleanupSockets();
					cleanupDelay();
					this->BeginInvoke(gcnew scanRunStop(this, &UEMAuto::stopScanRun));
					this->BeginInvoke(gcnew UpdateDelStatus(this, &UEMAuto::DelStatUpdater), gcnew String("scanRunner.\n"));
				}

				if (cc_buffer[0] == '1')
				{
					rundel = 1;
				}
				else
				{
					rundel = 0;
				}

				if (rundel == 1)
				{
					curChar = cc_buffer[1];
					sizeDelayData = 0;

					while (curChar != '|')
					{
						sizeDelayData++;
						tracker++;
						curChar = cc_buffer[tracker];
					}

					delaydata = new char[sizeDelayData + 1];

					for (a = 1; a <= sizeDelayData + 1; a++)
					{
						delaydata[a - 1] = cc_buffer[a];
					}

					delaydata[sizeDelayData] = '\0';

					memset(cc_buffer, 0, sizeof(cc_buffer));

					curDistPoint = std::stod(delaydata) / mm_to_ps + curZero;

					this->BeginInvoke(gcnew UpdateDelStatus(this, &UEMAuto::DelStatUpdater), gcnew String("Data received and moving delay stage to position "  ".\n"));
					this->BeginInvoke(gcnew UpdateDelStatus(this, &UEMAuto::DelStatUpdater), gcnew String(delaydata));
					this->BeginInvoke(gcnew UpdateDelStatus(this, &UEMAuto::DelStatUpdater), gcnew String(".\n"));

					// send movement order
					//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
					// check for motion done status in text file

					while (completionValue != 1)
					{
						OpenFile.open("movementCommFile.txt");
						curLine = 0;
						completionValue = 0;

						if (OpenFile)
						{

							do
							{

								getline(OpenFile, line);

								if (curLine == 1)
								{
									completionStatus = line;
								}
								curLine++;

							} while (!OpenFile.eof());

							completionValue = std::stod(completionStatus);
						}
						System::Threading::Thread::Sleep(5000);
					}

					System::Threading::Thread::Sleep(50);
					cc_buffer[0] = '1\0';

					connectHealth = send(camcomm_client, cc_buffer, sizeof(cc_buffer), 0);
					
					if (connectHealth == SOCKET_ERROR)
					{
						cleanupSockets();
						cleanupDelay();
						this->BeginInvoke(gcnew scanRunStop(this, &UEMAuto::stopScanRun));
						this->BeginInvoke(gcnew UpdateDelStatus(this, &UEMAuto::DelStatUpdater), gcnew String("scanRunner.\n"));
					}

					memset(cc_buffer, 0, sizeof(cc_buffer));
				}

				System::Threading::Thread::Sleep(1000);

			}

		}

		/* PauseButton_Click
			Sets the pause state if another button has not already been pressed.
		*/
		private: System::Void PauseButton_Click(System::Object^ sender, System::EventArgs^ e) 
		{
	
			if (butPressMeantime != 1)
			{
				runStat = 2;
				butPressMeantime = 1;
				this->pauseButton->ForeColor.Red;
				this->pauseButton->Refresh();
				this->playRun->ForeColor.Black;
				this->playRun->Refresh();
			}

		}

		/* PlayRun_Click
			Resumes the scan if another button has not already been pressed.
		*/
		private: System::Void PlayRun_Click(System::Object^ sender, System::EventArgs^ e) 
		{

			if (butPressMeantime != 1)
			{
				runStat = 1;
				butPressMeantime = 1;
				this->pauseButton->ForeColor.Black;
				this->pauseButton->Refresh();
				this->playRun->ForeColor.AliceBlue;
				this->playRun->Refresh();
			}

		}

		/* StopButton_Click
			Stops the scan.
		*/
		private: System::Void StopButton_Click(System::Object^ sender, System::EventArgs^ e) 
		{

			runStat = 3;
			butPressMeantime = 1;

		}

		/* PsIndicator_CheckedChanged
			Adjusts the unit used for our delay values to ps
		*/
		private: System::Void PsIndicator_CheckedChanged(System::Object^ sender, System::EventArgs^ e) 
		{

			if (this->psIndicator->Checked == TRUE)
			{
				this->nsIndicator->Checked = FALSE;
				units[1] = 'p';
			}
			else
			{
				this->nsIndicator->Checked = TRUE;
				units[1] = 'n';
			}

		}

		/* NsIndicator_CheckedChanged
			Adjusts the unit used for our delay values to ns
		*/
		private: System::Void NsIndicator_CheckedChanged(System::Object^ sender, System::EventArgs^ e) 
		{

			if (this->nsIndicator->Checked == TRUE)
			{
				this->psIndicator->Checked = FALSE;
				units[1] = 'n';
			}
			else
			{
				this->psIndicator->Checked = TRUE;
				units[1] = 'p';
			}

		}

		private: System::Void cleanupDelay()
		{
			this->statusWindow->AppendText("Cleaning up delay stage scripts.\n");
			// Send signal to kill delay stage scripts and associated threads
				//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

			std::ofstream OpenFile;

			OpenFile.open("connectStatFile.txt");

			OpenFile << "2";

			OpenFile.close();
			
			delayConnected = 0;
		}

		/* BrowseFilePath_Click
			Browses for a directory to store DM images in
		*/
		private: System::Void BrowseFilePath_Click(System::Object^ sender, System::EventArgs^ e) 
		{
		
			FolderBrowserDialog^ imgDirectory = gcnew FolderBrowserDialog;

			imgDirectory->Description = "Select your dm4 file location.";
			imgDirectory->ShowNewFolderButton = true;

			imgDirectory->ShowDialog();

			this->fileSavePath->Text = imgDirectory->SelectedPath;
			this->fileSavePath->Refresh();

		}

		/* DelayValueUpdater_DoWork and associated delegate functions
			Handles all the work for updating the delay stage value on the delay stage side.

			delDistUpdater-distDelUpdater delegate pair: updates the position of the delay stage
			delTimeUpdater-timeDelUpdater delegate pair: updates the time value
			killDelUpdater-delKillUpdater delegate pair: kills the updater if there is an issue with Soloist
		*/
		delegate System::Void delDistUpdater();
		System::Void distDelUpdater()
		{
			this->delayPosDist->Text = gcnew String(std::to_string(positionFeedback).c_str());
		}
		delegate System::Void delTimeUpdater();
		System::Void timeDelUpdater()
		{
			this->delayPosTime->Text = gcnew String(std::to_string(curdelTime).c_str());
		}
		delegate System::Void killDelUpdater();
		System::Void delKillUpdater()
		{
			this->delayValueUpdater->CancelAsync();
		}
		private: System::Void DelayValueUpdater_DoWork(System::Object^ sender, System::ComponentModel::DoWorkEventArgs^ e)
		{
			std::ifstream OpenFile;
			std::string line;

			while (true)
			{
				OpenFile.open("positionFile.txt");

				if (OpenFile)
				{
					getline(OpenFile, line);
					positionFeedback = std::stod(line); //!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Watch for units!
				}
				else// find some way to error out!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
				{
					
					this->BeginInvoke(gcnew killDelUpdater(this, &UEMAuto::delKillUpdater));
					this->BeginInvoke(gcnew UpdateDelStatus(this, &UEMAuto::DelStatUpdater), gcnew String("delayValueUpdater.\n"));
					cleanupDelay();
				}
				curdelTime = (positionFeedback - curZero) * mm_to_ps;
				this->BeginInvoke(gcnew delDistUpdater(this, &UEMAuto::distDelUpdater));
				this->BeginInvoke(gcnew delTimeUpdater(this, &UEMAuto::timeDelUpdater));
				System::Threading::Thread::Sleep(100);
			}

		}

		private: System::Void RepeatBox_TextChanged(System::Object^ sender, System::EventArgs^ e)
		{

			
			if (System::String::IsNullOrEmpty(this->RepeatBox->Text))
			{
				repeatValue = 0;
			}
			else
			{
				repeatValue = std::stoi((msclr::interop::marshal_as<std::string>(this->RepeatBox->Text).c_str())); // casts the value in RepeatBox to int
				if (repeatValue < 0)
				{

					repeatValue = 0;
				
				}
			}
			this->RepeatBox->Text = gcnew String(std::to_string(repeatValue).c_str()); // sets the value in RepeatBox to repeatValue. Defensively protects against invalid values by displaying incorrectly typed values as their ASCII to numerical conversion.
			
		}

		private: System::Void DelayIPSetting_TextChanged(System::Object^ sender, System::EventArgs^ e) 
		{
			
			this->servIP->Text = this->DelayIPSetting->Text;

		}

		private: System::Void timeZeroPositionSetting_TextChanged(System::Object^ sender, System::EventArgs^ e) 
		{

			if (System::String::IsNullOrEmpty(this->timeZeroPositionSetting->Text))
			{
				curZero = 0;
			}
			else
			{
				curZero = std::stoi((msclr::interop::marshal_as<std::string>(this->timeZeroPositionSetting->Text).c_str())); // casts the value in timeZeroPositionSetting to int
				if (curZero < 0)
				{

					curZero = 0;

				}
			}
			this->timeZeroPositionSetting->Text = gcnew String(std::to_string(curZero).c_str()); // sets the value in timeZeroPositionSetting to curZero. Defensively protects against invalid values by displaying incorrectly typed values as their ASCII to numerical conversion.

		}

		private: System::Void SaveSettingsButton_Click(System::Object^ sender, System::EventArgs^ e) 
		{

			WriteSettings writer;

			std::string saveTimeZero = std::to_string(curZero);
			std::string saveSpeed = msclr::interop::marshal_as<std::string>(this->delaySpeedSetting->Text);
			std::string saveIP = msclr::interop::marshal_as<std::string>(this->DelayIPSetting->Text);
			std::string customIdx = msclr::interop::marshal_as<std::string>(this->customMenuIndex->Text);
			std::string scanScriptIdx = msclr::interop::marshal_as<std::string>(this->scanScriptIndex->Text);
			std::string selectiveInSituIdx = msclr::interop::marshal_as<std::string>(this->selectiveInSituIndex->Text);

			writer.WriteSet("UEMtomatonConfig.txt",saveTimeZero,saveSpeed,saveIP,customIdx,scanScriptIdx,selectiveInSituIdx);

		}

		private: System::Void loadSettingsButton_Click(System::Object^ sender, System::EventArgs^ e) 
		{

			std::string acqTimeZero;
			std::string acqSpeed;
			std::string acqIP;
			std::string customIdx;
			std::string scanScriptIdx;
			std::string selectiveInSituIdx;

			std::ifstream OpenFile;

			std::string line;
			int curLine = 0;

			OpenFile.open("UEMtomatonConfig.txt");

			if (OpenFile)
			{

				do
				{

					getline(OpenFile, line);

					if (curLine == 0)
					{
						acqTimeZero = line;
						curLine = 1;
					}
					else if (curLine == 1)
					{
						acqSpeed = line;
						curLine = 2;
					}
					else if (curLine == 2)
					{
						acqIP = line;
						curLine = 3;
					}
					else if (curLine == 3)
					{
						customIdx = line;
						curLine = 4;
					}
					else if (curLine == 4)
					{
						scanScriptIdx = line;
						curLine = 5;
					}
					else if (curLine == 5)
					{
						selectiveInSituIdx = line;
					}

				} while (!OpenFile.eof());

				curZero = std::stod(acqTimeZero);
				this->delaySpeedSetting->Text = gcnew String(acqSpeed.c_str());
				this->DelayIPSetting->Text = gcnew String(acqIP.c_str());
				this->servIP->Text = this->DelayIPSetting->Text;
				this->customMenuIndex->Text = gcnew String(customIdx.c_str());
				this->scanScriptIndex->Text = gcnew String(scanScriptIdx.c_str());
				this->selectiveInSituIndex->Text = gcnew String(selectiveInSituIdx.c_str());

			}
			else
			{

				String^ upStat = gcnew String("UEMtomatonConfig.txt not found. Settings unchanged.\r\n");
				this->camStat->AppendText(upStat);

			}

			OpenFile.close();

		}

		private: System::Void DefaultSettingsRestore_Click(System::Object^ sender, System::EventArgs^ e) 
		{

			curZero = 300; // mm
			this->timeZeroPositionSetting->Text = gcnew String(std::to_string(curZero).c_str());
			this->DelayIPSetting->Text = gcnew String("192.168.0.3");
			this->servIP->Text = this->DelayIPSetting->Text;
			this->customMenuIndex->Text = gcnew String("8");
			this->scanScriptIndex->Text = gcnew String("2");
			this->selectiveInSituIndex->Text = gcnew String("4");

		}

		private: System::Void delayConnect_Click(System::Object^ sender, System::EventArgs^ e) 
		{

			// Initialize IronPython!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
			spawnl(P_NOWAIT, "DelayStageCommScript.exe", "DelayStageCommScript.exe", NULL);

			// This is the camera side --> don't need to open IronPython when it's already started by the delay side.

			this->delayValueUpdater->RunWorkerAsync();

			this->statusWindow->AppendText("Delay stage connected.\r\n");
			delayConnected = 1;

		}

		/// <summary>
		/// SELECTIVE IN SITU CODE HERE
		/// </summary>

		private: System::Void SII_acq_Time_TextChanged(System::Object^ sender, System::EventArgs^ e) 
		{

			SII_acq_time = std::stod(msclr::interop::marshal_as<std::string>(this->SII_acq_Time->Text));

			if (SII_acq_time > 0)
			{
				SII_time_between = (SII_images_skipped + 1) * SII_acq_time;
				this->SII_time_Between->Text = gcnew String(SII_time_between.ToString());

				if (SII_total_saves > 0)
				{
					SII_total_time = SII_total_saves * SII_acq_time * (SII_images_skipped + 1);
					this->SII_total_Time->Text = gcnew String(SII_total_time.ToString());
				}
				else
				{
					SII_total_time = -1;
				}
			}
			else
			{
				SII_total_time = -1;
				SII_acq_time = -1;
				this->SII_acq_Time->Text = gcnew String("-1");
				this->SII_time_Between->Text = gcnew String("-1");
				this->SII_total_Time->Text = gcnew String("-1");
			}

		}

		private: System::Void SII_skipped_TextChanged(System::Object^ sender, System::EventArgs^ e) 
		{
			
			SII_images_skipped = std::stoi(msclr::interop::marshal_as<std::string>(this->SII_skipped->Text));

			if (SII_images_skipped < 0)
			{

				SII_images_skipped = 0;

			}

			if (SII_acq_time > 0)
			{

				SII_time_between = (SII_images_skipped + 1) * SII_acq_time;
				this->SII_time_Between->Text = gcnew String(SII_time_between.ToString());

			}

			if (SII_total_saves > 0)
			{
				SII_total_time = SII_total_saves * SII_acq_time * (SII_images_skipped + 1);
				this->SII_total_Time->Text = gcnew String(SII_total_time.ToString());
			}
			else
			{
				SII_total_time = -1;
			}

		}

		private: System::Void SII_total_Saves_TextChanged(System::Object^ sender, System::EventArgs^ e) 
		{

			SII_total_saves = std::stoi(msclr::interop::marshal_as<std::string>(this->SII_total_Saves->Text));

			if (SII_acq_time > 0)
			{
				SII_total_time = SII_total_saves * SII_acq_time * (SII_images_skipped + 1);
				this->SII_total_Time->Text = gcnew String(SII_total_time.ToString());
			}
			else
			{
				SII_total_time = -1;
			}

		}

		private: System::Void browseSII_Click(System::Object^ sender, System::EventArgs^ e) 
		{

			FolderBrowserDialog^ imgDirectory = gcnew FolderBrowserDialog;

			imgDirectory->Description = "Select your dm4 file location.";
			imgDirectory->ShowNewFolderButton = true;

			imgDirectory->ShowDialog();

			this->filepathSelInSitu->Text = imgDirectory->SelectedPath;
			this->filebaseSelInSitu->Refresh();

		}

		private: System::Void selectiveInSitu_Click(System::Object^ sender, System::EventArgs^ e) 
		{
			
			String^ upStat;
			HWND hWnd;
			HWND hWnd2;

			WriteSII SIICommWriter;

			upStat = "Updating DM communication for selective in situe mode.\r\n";
			this->SII_status_box->AppendText(upStat);
			// UPDATE CAMERA COMMUNICATION DOCUMENT
			SIICommWriter.WriteData("C:\\SIIFileInput.txt", msclr::interop::marshal_as<std::string>(this->filepathSelInSitu->Text), msclr::interop::marshal_as<std::string>(this->filebaseSelInSitu->Text), std::to_string(SII_images_skipped), std::to_string(SII_total_saves), std::to_string(SII_acq_time)); //"C:\\TestFile\\SIIFileInput.txt", msclr::interop::marshal_as<std::string>(this->filepathSelInSitu->Text), msclr::interop::marshal_as<std::string>(this->filebaseSelInSitu->Text), std::to_string(SII_images_skipped), std::to_string(SII_total_saves)

			HWND hFoundWnd = NULL;
			WindowSearcher finder;
			hFoundWnd = finder.FocusWindow();
			// !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! SELECTIVE INSITU AHK
			if (hFoundWnd != NULL)
			{
				// move to foreground
				this->WindowState = System::Windows::Forms::FormWindowState::Minimized;
				this->WindowState = System::Windows::Forms::FormWindowState::Normal; // this is the dumbest hack I've tried and I'm almost ashamed it works. Almost.
				//SetWindowPos(hWnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE);
				SetForegroundWindowInternal(hFoundWnd);
				//SetActiveWindow(hWnd);
				spawnl(P_NOWAIT, "SelectiveImaging.exe", "SelectiveImaging.exe", NULL);

				System::Threading::Thread::Sleep(30);

				this->WindowState = System::Windows::Forms::FormWindowState::Minimized;
				this->WindowState = System::Windows::Forms::FormWindowState::Normal; // facepalm
			}
			else
			{
				String^ upStat = gcnew String("Window containing \"DigitalMicrograph\" title was not found.\r\n");
				this->camStat->AppendText(upStat);
			}

		}

};

}