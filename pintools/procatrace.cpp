/*BEGIN_LEGAL 
Intel Open Source License 

Copyright (c) 2002-2017 Intel Corporation. All rights reserved.
 
Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.  Redistributions
in binary form must reproduce the above copyright notice, this list of
conditions and the following disclaimer in the documentation and/or
other materials provided with the distribution.  Neither the name of
the Intel Corporation nor the names of its contributors may be used to
endorse or promote products derived from this software without
specific prior written permission.
 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE INTEL OR
ITS CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
END_LEGAL */
//
// This tool traces memory access for a set of functions
//

#include <fstream>
#include <iostream>
#include <vector>
#include <algorithm>
#include <string>
#include "pin.H"

//ofstream outFile;
vector<string> klist;

/* ===================================================================== */
// Command line switches
/* ===================================================================== */
KNOB<string> KnobKernelListFile(KNOB_MODE_WRITEONCE, "pintool", "klist", "kernel_list.txt", "path to kernel list file");

/* ===================================================================== */
// Helper function
/* ===================================================================== */
bool kcontains(const string kname)
{
    return find(klist.begin(), klist.end(), kname) != klist.end();
}

void klist_init(vector<string> *klist)
{
    ifstream klfile(KnobKernelListFile.Value().c_str());
    string kernel;

    while(klfile >> kernel)
    {
        klist->push_back(kernel);
    }
}

// Print a memory read record
VOID RecordMemRead(THREADID tid, ADDRINT funcaddr, VOID * memaddr)
{
    string funcname = RTN_FindNameByAddress(funcaddr);

    // verify single thread
    if (tid != 0) {
        cerr << "- Error: Function " << funcname << " is using thread " << tid << endl;
        PIN_Detach();
    }

    //outFile << funcname << " R " << hex << memaddr << endl;
    cout << funcname << " R " << hex << memaddr << endl;
}

// Print a memory write record
VOID RecordMemWrite(THREADID tid, ADDRINT funcaddr, VOID * memaddr)
{
    string funcname = RTN_FindNameByAddress(funcaddr);

    // verify single thread
    if (tid != 0) {
        cerr << "- Error: Function " << funcname << " is using thread " << tid << endl;
        PIN_Detach();
    }

    //outFile << funcname << " W " << hex << memaddr << endl;
    cout << funcname << " W " << hex << memaddr << endl;
}

// Pin calls this function every time a new rtn is executed
VOID Routine(RTN rtn, VOID *v)
{
    if (kcontains(RTN_Name(rtn)))
    {
        cerr << "instrumenting " << RTN_Name(rtn) << endl;
        RTN_Open(rtn);

        // For each instruction of the routine
        for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins))
        {
            UINT32 memOperands = INS_MemoryOperandCount(ins);

            // Iterate over each memory operand of the instruction.
            for (UINT32 memOp = 0; memOp < memOperands; memOp++)
            {
                if (INS_MemoryOperandIsRead(ins, memOp))
                {
                    INS_InsertPredicatedCall(
                        ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
                        IARG_THREAD_ID,
                        IARG_ADDRINT, RTN_Address(rtn), 
                        IARG_MEMORYOP_EA, memOp,
                        IARG_END);
                }
                // Note that in some architectures a single memory operand can be 
                // both read and written (for instance incl (%eax) on IA-32)
                // In that case we instrument it once for read and once for write.
                if (INS_MemoryOperandIsWritten(ins, memOp))
                {
                    INS_InsertPredicatedCall(
                        ins, IPOINT_BEFORE, (AFUNPTR)RecordMemWrite,
                        IARG_THREAD_ID,
                        IARG_ADDRINT, RTN_Address(rtn), 
                        IARG_MEMORYOP_EA, memOp,
                        IARG_END);
                }
            }
        }

        RTN_Close(rtn);
    }
}

// This function is called when the application exits
// It prints the name and count for each procedure
VOID Fini(INT32 code, VOID *v)
{
    //outFile.close();
}

/* ===================================================================== */
/* Print Help Message                                                    */
/* ===================================================================== */

INT32 Usage()
{
    cerr << "This Pintool traces memory access for specific function" << endl;
    cerr << endl << KNOB_BASE::StringKnobSummary() << endl;
    return -1;
}

/* ===================================================================== */
/* Main                                                                  */
/* ===================================================================== */

int main(int argc, char * argv[])
{
    // initialize kernel list
    klist_init(&klist);

    // Initialize symbol table code, needed for rtn instrumentation
    PIN_InitSymbols();

    //outFile.open("/tmp/procatrace.out");

    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();

    // Register Routine to be called to instrument rtn
    RTN_AddInstrumentFunction(Routine, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
