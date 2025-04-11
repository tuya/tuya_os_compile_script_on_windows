/******************************************************************************

 @file  cc23x0_app_freertos.cmd

 @brief cc23x0R5 linker configuration file for FreeRTOS
        with Code Composer Studio.

        Imported Symbols
        Note: Linker defines are located in the CCS IDE project by placing them
        in
        Properties->Build->Linker->Advanced Options->Command File Preprocessing.

        ICALL_RAM0_START:   RAM start of BLE stack.
        ICALL_STACK0_START: Flash start of BLE stack.
        PAGE_AlIGN:         Align BLE stack boundary to a page boundary.
                            Aligns to Flash word boundary by default.

 Group: WCS, BTS
 Target Device: cc23xx

 ******************************************************************************
 
 Copyright (c) 2017-2023, Texas Instruments Incorporated
 All rights reserved.

 Redistribution and use in source and binary forms, with or without
 modification, are permitted provided that the following conditions
 are met:

 *  Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.

 *  Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.

 *  Neither the name of Texas Instruments Incorporated nor the names of
    its contributors may be used to endorse or promote products derived
    from this software without specific prior written permission.

 THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
 AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
 THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
 PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
 OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
 OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
 EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

 ******************************************************************************
 
 *****************************************************************************/


/*******************************************************************************
 * CCS Linker configuration
 */

/* Override default entry point.                                             */
--entry_point=resetISR

/* Retain interrupt vector table variable                                    */
--retain "*(.resetVecs)"

/* Suppress warnings and errors:                                             */
/* - 10063: Warning about entry point not being _c_int00                     */
/* - 16011, 16012: 8-byte alignment errors. Observed when linking in object  */
/*   files compiled using Keil (ARM compiler)                                */
--diag_suppress=10063,16011,16012
--heap_size=0
--stack_size=1024
//--stack_size=1400
/* The following command line options are set as part of the CCS project.    */
/* If you are building using the command line, or for some reason want to    */
/* define them here, you can uncomment and modify these lines as needed.     */
/* If you are using CCS for building, it is probably better to make any such */
/* modifications in your CCS project and leave this file alone.              */
/*                                                                           */
/* --heap_size=0                                                             */
/* --stack_size=256                                                          */
/* --library=rtsv7M3_T_le_eabi.lib                                           */

/* Set severity of diagnostics to Remark instead of Warning                  */
/* - 10068: Warning about no matching log_ptr* sections                      */
--diag_remark=10068

/* The starting address of the application.  Normally the interrupt vectors  */
/* must be located at the beginning of the application. Flash is 128KB, with */
/* sector length of 4KB                                                      */
/*******************************************************************************
 * Memory Sizes
 */
// Flash
#define FLASH_SIZE   			0x00080000
#define FLASH_BASE   			0x00000000
// RAM
#define RAM_SIZE     			0x00010000
#define RAM_BASE     			0x20000000
// S2RRAM
#define S2RRAM_SIZE  			0x1000
#define S2RRAM_BASE  			0x40098000
// CCFG
#define CCFG_SIZE    			0x800
#define CCFG_BASE    			0x4E020000
// App
#define APP_NVS_SIZE		    0x5000
#define APP_NVS_BASE		    (FLASH_SIZE - APP_NVS_SIZE)

#if defined(OAD_APP_OFFCHIP) || defined(OAD_APP_ONCHIP) || defined(OAD_PERSISTENT) || defined(OAD_DUAL_IMAGE)
#define MCU_HDR_SIZE    0x100
#define MCUBOOT_BASE    FLASH_BASE
#define MCUBOOT_SIZE    0x3000
#define APP_HDR_BASE    APP_HDR_ADDR
#define APP_BASE        (APP_HDR_BASE + MCU_HDR_SIZE)
#endif //defined(OAD_APP_OFFCHIP) || defined(OAD_APP_ONCHIP) || defined(OAD_PERSISTENT) || defined(OAD_DUAL_IMAGE)

#ifdef OAD_DUAL_IMAGE
#define APP_SIZE        (0x3C000 - MCU_HDR_SIZE)
#endif //OAD_DUAL_IMAGE

/*******************************************************************************
 * Memory Definitions
 ******************************************************************************/

/*******************************************************************************
 * RAM
 */
#define RAM_START      (RAM_BASE)
#ifdef ICALL_RAM0_START
  #define RAM_END      (ICALL_RAM0_START - 1)
#else
  #define RAM_END      (RAM_BASE + RAM_SIZE - 1)
#endif /* ICALL_RAM0_START */

/*******************************************************************************
 * Flash
 */

#define FLASH_START                FLASH_BASE
#define WORD_SIZE                  4

#define PAGE_SIZE                  0x800

#ifdef PAGE_ALIGN
  #define FLASH_MEM_ALIGN          PAGE_SIZE
#else
  #define FLASH_MEM_ALIGN          WORD_SIZE
#endif /* PAGE_ALIGN */

#define PAGE_MASK                  0xFFFFE000

/*******************************************************************************
 * Stack
 */

/* Create global constant that points to top of stack */
/* CCS: Change stack size under Project Properties    */
__STACK_TOP = __stack + __STACK_SIZE;

/*******************************************************************************
 * ROV
 * These symbols are used by ROV2 to extend the valid memory regions on device.
 * Without these defines, ROV will encounter a Java exception when using an
 * autosized heap. This is a posted workaround for a known limitation of
 * RTSC/rta. See: https://bugs.eclipse.org/bugs/show_bug.cgi?id=487894
 *
 * Note: these do not affect placement in RAM or FLASH, they are only used
 * by ROV2, see the BLE Stack User's Guide for more info on a workaround
 * for ROV Classic
 *
 */
__UNUSED_SRAM_start__ = RAM_BASE;
__UNUSED_SRAM_end__ = RAM_BASE + RAM_SIZE;

__UNUSED_FLASH_start__ = FLASH_BASE;
__UNUSED_FLASH_end__ = FLASH_BASE + FLASH_SIZE;

/*******************************************************************************
 * Main arguments
 */

/* Allow main() to take args */
/* --args 0x8 */

/*******************************************************************************
 * System Memory Map
 ******************************************************************************/
MEMORY
{
    /* EDITOR'S NOTE:
     * the FLASH and SRAM lengths can be changed by defining
     * ICALL_STACK0_START or ICALL_RAM0_START in
     * Properties->ARM Linker->Advanced Options->Command File Preprocessing.
     */

#if defined(OAD_APP_OFFCHIP)|| defined(OAD_APP_ONCHIP) || defined(OAD_PERSISTENT) || defined(OAD_DUAL_IMAGE)

    MCUBOOT_SLOT(RX)       : origin = MCUBOOT_BASE        ,length = MCUBOOT_SIZE
    APP_HDR_SLOT(RX)       : origin = APP_HDR_BASE        ,length = MCU_HDR_SIZE
    APP_SLOT (RX)          : origin = APP_BASE            ,length = APP_SIZE

#else //Without mcuboot

    FLASH (RX)   : origin = 0x0,      length = (FLASH_SIZE - APP_NVS_SIZE)

#endif //defined(OAD_APP_OFFCHIP)|| defined(OAD_APP_ONCHIP) || defined(OAD_PERSISTENT)

    CUSTOM_APP_NVS_SLOT(RX) : origin = APP_NVS_BASE ,length = APP_NVS_SIZE

    /* Application uses internal RAM for data */
    SRAM (RWX) : origin = RAM_START, length = (RAM_END - RAM_START + 1)

    /* S2RRAM is intended for the S2R radio module, but it can also be used by
     * the application with some limitations. Please refer to the s2rram example.
     */
    S2RRAM (RW) : origin = S2RRAM_BASE, length = S2RRAM_SIZE

    CCFG (RW) : origin = CCFG_BASE, length = CCFG_SIZE

    /* Explicitly placed off target for the storage of logging data.
     * The ARM memory map allocates 1 GB of external memory from 0x60000000 - 0x9FFFFFFF.
     * Unlikely that all of this will be used, so we are using the upper parts of the region.
     * ARM memory map: https://developer.arm.com/documentation/ddi0337/e/memory-map/about-the-memory-map*/
    LOG_DATA (R) : origin = 0x90000000, length = 0x40000        /* 256 KB */
    LOG_PTR  (R) : origin = 0x94000008, length = 0x40000        /* 256 KB */
}

/*******************************************************************************
 * Section Allocation in Memory
 ******************************************************************************/
SECTIONS
{
#if defined(OAD_APP_OFFCHIP) || defined(OAD_APP_ONCHIP) || defined(OAD_PERSISTENT) || defined(OAD_DUAL_IMAGE)

	.primary_hdr    :   > APP_HDR_SLOT, type = NOLOAD

#if defined(OAD_APP_OFFCHIP) || defined(OAD_APP_ONCHIP) || defined(OAD_DUAL_IMAGE)

    .resetVecs      :   > APP_BASE
    .text           :   > APP_SLOT
    .const          :   > APP_SLOT
    .constdata      :   > APP_SLOT
    .rodata         :   > APP_SLOT
    .binit          :   > APP_SLOT
    .cinit          :   > APP_SLOT
    .pinit          :   > APP_SLOT
    .init_array     :   > APP_SLOT
    .emb_text       :   > APP_SLOT

#endif //defined(OAD_APP_OFFCHIP) || defined(OAD_APP_ONCHIP) || defined(OAD_DUAL_IMAGE)

#else
  .resetVecs      :   >  FLASH_START
  .text           :   >> FLASH
  .TI.ramfunc     : {} load=FLASH, run=SRAM, table(BINIT)
  .const          :   >> FLASH
  .constdata      :   >> FLASH
  .rodata         :   >> FLASH
  .binit          :   > FLASH
  .cinit          :   >  FLASH
  .pinit          :   >> FLASH
  .init_array     :   >  FLASH
  .emb_text       :   >> FLASH

#endif //defined(OAD_APP_OFFCHIP) || defined(OAD_APP_ONCHIP) || defined(OAD_PERSISTENT) || defined(OAD_DUAL_IMAGE)

  .ccfg           :   > CCFG
  .ramVecs        :   > SRAM, type = NOLOAD, ALIGN(256)
  .data           :   > SRAM
  .bss            :   > SRAM
  .sysmem         :   > SRAM
  .nonretenvar    :   > SRAM
  .heap           :   > SRAM
  .stack          :   > SRAM (HIGH)

  /* Placing the section .s2rram in S2RRAM region. Only uninitialized
   * objects may be placed in this section.
   */
  .s2rram         :   > S2RRAM, type = NOINIT

  .log_data       :   > LOG_DATA, type = COPY
  .log_ptr        : { *(.log_ptr*) } > LOG_PTR align 4, type = COPY
}
