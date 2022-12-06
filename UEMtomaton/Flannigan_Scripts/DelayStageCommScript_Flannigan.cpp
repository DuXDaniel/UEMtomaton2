#pragma once
#pragma comment (lib, "Ws2_32.lib")
#pragma comment (lib, "kernel32.lib")
#pragma comment (lib, "user32.lib")
#pragma comment (lib, "SoloistC.lib")
#pragma comment (lib, "SoloistC64.lib")

#include <iostream>
#include <sstream>
#include <fstream>
#include <thread>
using namespace std;
using namespace std::chrono_literals;
#include "Soloist.h"

class WriteConnectStat
{
    public:
        void WriteData(std::string val1)
        {

            std::ofstream OpenFile;

            OpenFile.open("connectStatFile.txt");
            OpenFile << val1;
            OpenFile.close();

            return;
        }

        std::string ConnectStat()
        {

            std::ifstream OpenFile;

            std::string line;

            OpenFile.open("connectStatFile.txt");
            getline(OpenFile, line);

            return line;
        }
};

class WriteMovement
{
    public:
        void WriteData(std::string val1, std::string val2)
        {

            std::ofstream OpenFile;

            OpenFile.open("movementCommFile.txt");
            OpenFile << val1 + "\n";
            OpenFile << val2;
            OpenFile.close();

            return;
        }
};

class WritePosition
{
    public:
        void WriteData(std::string val1)
        {

            std::ofstream OpenFile;

            OpenFile.open("positionFile.txt");
            OpenFile << val1;
            OpenFile.close();

            return;
        }
};

class DelayComm
{
    public:
        double positionFeedback;
        int delayConnected;

        WriteConnectStat connectWriter;
        WriteMovement movementWriter;
        WritePosition positionWriter;

        // Handles to all the connected Soloists
        SoloistHandle* handles;
        // Handle to give access to Soloist
        SoloistHandle handle = NULL;
        DWORD handleCount = 0;

        DelayComm() // constructor for all values that need to be initialized
        {
            this->delayConnected = 0;
            this->connectWriter.WriteData("1");
            this->positionFeedback = 0;
        }
        /// Clean up any resources being used.
        ~DelayComm()
        {
            cleanupSoloist();
        }
        
        void cleanupSoloist()
        {
            if (this->handleCount > 0) 
            {
                if (!SoloistDisconnect(this->handles)) 
                { 
                    printSoloistError(); 
                }

                this->delayConnected = 0;
            }
            
            this->connectWriter.WriteData("2");
        }

        void Init_Soloist() 
        {
            if (!SoloistConnect(&this->handles, &this->handleCount))
            {
                cleanupSoloist();
                return;
            }

            if (handleCount != 1)
            {
                cleanupSoloist();
                return;
            }
            this->handle = this->handles[0];

            if (!SoloistMotionEnable(this->handle))
            {
                cleanupSoloist();
                return;
            }
        }

        /* ScanRunner_DoWork and associated delegate functions
            Handles all the work for organizing the individual steps in a run.
        */
        void ScanRunner_DoWork() 
        {
            std::ifstream OpenFile;

            std::string posMove;
            std::string moveStat;

            while (delayConnected == 1)
            {

                // Await new movement order
                OpenFile.open("movementCommFile.txt");

                if (OpenFile)
                {
                    getline(OpenFile, posMove);
                    getline(OpenFile, moveStat);
                }

                // curDistPoint = std::stod(delaydata) / mm_to_ps + curZero;

                if (moveStat == "0")
                {
                    if (!SoloistMotionMoveAbs(this->handle, std::stod(posMove), 50))
                    {
                        cleanupSoloist();
                    }
                    else
                    {
                        if (!SoloistMotionWaitForMotionDone(this->handle, WAITOPTION_MoveDone, -1, NULL))
                        {
                            cleanupSoloist();
                        }
                        this->movementWriter.WriteData(posMov, "1")
                    }
                }

                std::this_thread::sleep_for(1000ms);

                this->delayConnected = std::stoi(connectWriter.ConnectStat());

            }

        }

        /* DelayValueUpdater_DoWork and associated delegate functions
            Handles all the work for updating the delay stage value on the delay stage side.
        */
        void DelayValueUpdater_DoWork()
        {

            while (delayConnected == 1)
            {
                if (!SoloistStatusGetItem(this->handle, STATUSITEM_PositionFeedback, &this->positionFeedback))
                {
                    cleanupSoloist();
                }
                
                this->positionWriter.WriteData(std::to_string(positionFeedback));
                
                std::this_thread::sleep_for(100ms);

                this->delayConnected = std::stoi(connectWriter.ConnectStat());
            }

        }
};

int main()
{
    WriteConnectStat connectWriter;
    connectWriter.WriteData("1");
    int delayConnected = std::stoi(connectWriter.ConnectStat());

    DelayComm communicator;
    communicator.Init_Soloist();
    
    std::thread scanRunner(&DelayComm::ScanRunner_DoWork, &communicator);
    std::thread delayValueUpdater(&DelayComm::DelayValueUpdater_DoWork, &communicator);
    while (delayConnected == 1)// delayConnected is not equiv to 2
    {
        delayConnected = std::stoi(connectWriter.ConnectStat());
    }
};