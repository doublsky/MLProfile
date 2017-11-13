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
#include <map>
#include <string>
#include "pin.H"

ofstream outFile;
map<string, UINT64> klist;     // pair<kernel_name, num_times_called>

/* ===================================================================== */
// Command line switches
/* ===================================================================== */
KNOB<string> KnobKernelListFile(KNOB_MODE_WRITEONCE, "pintool", "klist", "kernel_list.txt", "path to kernel list file");
KNOB<string> KnobOutputFile(KNOB_MODE_WRITEONCE, "pintool", "output", "stdout", "path to output file");

/* ===================================================================== */
// Helper function
/* ===================================================================== */
bool kcontains(const string kname)
{
    return (klist.find(kname) != klist.end());
}

void klist_init(map<string, UINT64> *klist)
{
    ifstream klfile(KnobKernelListFile.Value().c_str());
    string kernel;

    while(klfile >> kernel)
    {
        pair<map<string, UINT64>::iterator, bool> ret;
        ret = klist->insert(pair<string, UINT64>(kernel, 0));
        if (ret.second == false)
        {
            PIN_ERROR("Duplicated kernel found in " + KnobKernelListFile.Value() + "\n");
        }
    }
}

// Print a memory read record
VOID RecordMemRead(THREADID tid, ADDRINT funcaddr, VOID * memaddr, UINT32 size)
{
    string funcname = RTN_FindNameByAddress(funcaddr);

    // verify single thread
    if (tid != 0) {
        cerr << "- Error: Function " << funcname << " is using thread " << tid << endl;
        PIN_Detach();
    }

    if (KnobOutputFile.Value() == "stdout") {
        cout << funcname << " " << dec << klist[funcname] << " R " << hex << memaddr << " " << dec << size << endl;
    } else {
        outFile << funcname << " " << dec << klist[funcname] << " R " << hex << memaddr << " " << dec << size << endl;
    }
}

// Print a memory write record
VOID RecordMemWrite(THREADID tid, ADDRINT funcaddr, VOID * memaddr, UINT32 size)
{
    string funcname = RTN_FindNameByAddress(funcaddr);

    // verify single thread
    if (tid != 0) {
        cerr << "- Error: Function " << funcname << " is using thread " << tid << endl;
        PIN_Detach();
    }

    if (KnobOutputFile.Value() == "stdout") {
        cout << funcname << " " << dec << klist[funcname] << " W " << hex << memaddr << " " << dec << size << endl;
    } else {
        outFile << funcname << " " << dec << klist[funcname] << " W " << hex << memaddr << " " << dec << size << endl;
    }
}

// Count how many times a routine gets called
VOID CountRoutine(UINT64* counter)
{
    (*counter)++;
}

// Pin calls this function every time a new rtn is executed
VOID Routine(RTN rtn, VOID *v)
{
    string original_rtnName = RTN_Name(rtn);
    string rtnName = PIN_UndecorateSymbolName(original_rtnName, UNDECORATION_NAME_ONLY);
    if (kcontains(rtnName))
    {
        cerr << "instrumenting " << rtnName << endl;
        RTN_Open(rtn);
        
        // Insert a call at the entry point of a routine to increment the call count
        RTN_InsertCall(rtn, IPOINT_BEFORE, (AFUNPTR)CountRoutine, IARG_PTR, &(klist[rtnName]), IARG_END);

        // For each instruction of the routine
        for (INS ins = RTN_InsHead(rtn); INS_Valid(ins); ins = INS_Next(ins))
        {
            UINT32 memOperands = INS_MemoryOperandCount(ins);

            // Iterate over each memory operand of the instruction.
            for (UINT32 memOp = 0; memOp < memOperands; memOp++)
            {
                // do not count prefetch instructions
                if (INS_IsPrefetch(ins))
                {
                    continue;
                }
                
                // do not count stack manipulation
                if (INS_IsStackRead(ins) || INS_IsStackWrite(ins))
                {
                    continue;
                }
                
                UINT32 memOpSize = INS_MemoryOperandSize(ins, memOp);
                
                if (INS_MemoryOperandIsRead(ins, memOp))
                {
                    INS_InsertPredicatedCall(
                        ins, IPOINT_BEFORE, (AFUNPTR)RecordMemRead,
                        IARG_THREAD_ID,
                        IARG_ADDRINT, RTN_Address(rtn), 
                        IARG_MEMORYOP_EA, memOp,
                        IARG_UINT32, memOpSize,
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
                        IARG_UINT32, memOpSize,
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
    outFile.close();
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


    // Initialize pin
    if (PIN_Init(argc, argv)) return Usage();
    outFile.open(KnobOutputFile.Value().c_str());

    // Register Routine to be called to instrument rtn
    RTN_AddInstrumentFunction(Routine, 0);

    // Register Fini to be called when the application exits
    PIN_AddFiniFunction(Fini, 0);
    
    // Start the program, never returns
    PIN_StartProgram();
    
    return 0;
}
