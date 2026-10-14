using System;
using System.Threading;
using System.Threading.Tasks;

namespace MiningSimulationUI
{
    class Program
    {
        static int coalDeposit = 2000;
        static int warehouse = 0;

        static SemaphoreSlim mineSemaphore = new SemaphoreSlim(2, 2);
        static SemaphoreSlim warehouseSemaphore = new SemaphoreSlim(1, 1);
        static object depositLock = new object();
        static object consoleLock = new object();
        static string[] minersStatus;
        static bool isSimulationRunning = true;

        static void Main(string[] args)
        {
            int numberOfMiners = 5;
            minersStatus = new string[numberOfMiners];
            for (int i = 0; i < numberOfMiners; i++) minersStatus[i] = "Oczekuje...";

            Console.Clear();
            Task uiTask = Task.Run(() => UpdateUI(numberOfMiners));

            Task[] miners = new Task[numberOfMiners];
            for (int i = 0; i < numberOfMiners; i++)
            {
                int minerId = i + 1;
                miners[i] = Task.Run(() => MinerWork(minerId));
            }

            Task.WaitAll(miners);
            isSimulationRunning = false;
            uiTask.Wait();

            Console.SetCursorPosition(0, numberOfMiners + 3);
            Console.WriteLine("Symulacja zakończona.");
        }

        static void UpdateUI(int numberOfMiners)
        {
            while (isSimulationRunning)
            {
                lock (consoleLock)
                {
                    Console.SetCursorPosition(0, 0);
                    Console.WriteLine($"Stan zloza: {coalDeposit} jednostek wegla".PadRight(50));
                    Console.WriteLine($"Stan magazynu: {warehouse} jednostek wegla".PadRight(50));
                    Console.WriteLine("".PadRight(50));

                    for (int i = 0; i < numberOfMiners; i++)
                    {
                        Console.WriteLine($"Gornik {i + 1}: {minersStatus[i]}".PadRight(50));
                    }
                }
                Thread.Sleep(10);
            }
        }

        static void ChangeStatus(int id, string status)
        {
            lock (consoleLock)
            {
                minersStatus[id - 1] = status;
            }
        }

        static void MinerWork(int id)
        {
            int capacity = 200;
            while (true)
            {
                int mined = 0;
                ChangeStatus(id, "Czeka na dostep do zloza...");
                mineSemaphore.Wait();
                lock (depositLock)
                {
                    if (coalDeposit == 0)
                    {
                        mineSemaphore.Release();
                        ChangeStatus(id, "Zakonczył prace.");
                        Thread.Sleep(1000);
                        break;
                    }
                    mined = Math.Min(capacity, coalDeposit);
                    coalDeposit -= mined;
                }
                ChangeStatus(id, "Wydobywa wegiel...");
                Thread.Sleep(mined * 10);
                mineSemaphore.Release();

                ChangeStatus(id, "Transportuje do magazynu...");
                Thread.Sleep(10000);

                ChangeStatus(id, "Czeka na rozladunek...");
                warehouseSemaphore.Wait();
                ChangeStatus(id, "Rozladowuje wegiel...");
                Thread.Sleep(mined * 10);
                warehouse += mined;
                warehouseSemaphore.Release();

                ChangeStatus(id, "Wraca do kopalni...");
                Thread.Sleep(10000);
            }
        }
    }
}
