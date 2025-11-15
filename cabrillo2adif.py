#!/usr/bin/env python3
"""
Cabrillo to ADIF Converter
Converts Cabrillo format amateur radio logs to ADIF format
"""

import sys
import argparse
import re
from datetime import datetime

# Precompiled regex pattern for QSO line with named capture groups
# Format: QSO: freq mode date time call_sent rst_sent exch_sent call_rcvd rst_rcvd exch_rcvd
QSO_PATTERN = re.compile(r'^QSO:\s+(?P<freq>\d+)\s+(?P<mode>\w+)\s+(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{4})\s+(?P<call_sent>\S+)\s+(?P<rst_sent>\d+)\s+(?P<exch_sent>\S+)\s+(?P<call_rcvd>\S+)\s+(?P<rst_rcvd>\d+)\s+(?P<exch_rcvd>\S+)')

def parse_qso_line(line, line_number):
    """
    Parse a QSO line from Cabrillo format using regex
    Returns a dictionary with QSO fields or None if invalid
    """
    match = QSO_PATTERN.match(line)
    
    if not match:
        sys.stderr.write(f"Error en línea {line_number}: {line.strip()}\n")
        return None
    
    try:
        # Extract fields from regex groups
        freq = match.group('freq')
        mode = match.group('mode')
        date = match.group('date')
        time = match.group('time')
        call_sent = match.group('call_sent')
        rst_sent = match.group('rst_sent')
        exch_sent = match.group('exch_sent')
        call_rcvd = match.group('call_rcvd')
        rst_rcvd = match.group('rst_rcvd')
        exch_rcvd = match.group('exch_rcvd')
        
        # Convert frequency from kHz to MHz for ADIF
        freq_mhz = str(float(freq) / 1000.0)
        
        # Convert mode
        mode_adif = "SSB" if mode == "PH" else mode
        
        # Parse date and time
        year = date[0:4]
        month = date[5:7]
        day = date[8:10]
        hour = time[0:2]
        minute = time[2:4]
        
        qso = {
            'freq': freq_mhz,
            'mode': mode_adif,
            'date': f"{year}{month}{day}",
            'time': f"{hour}{minute}",
            'call': call_rcvd,
            'rst_sent': rst_sent,
            'rst_rcvd': rst_rcvd,
            'stx': exch_sent,
            'srx': exch_rcvd
        }
        
        return qso
        
    except (ValueError, AttributeError) as e:
        sys.stderr.write(f"Error en línea {line_number}: {line.strip()}\n")
        return None

def cabrillo_to_adif(input_file, output_file):
    """
    Convert a Cabrillo file to ADIF format
    """
    callsign = None
    grid_locator = None
    name = None
    contest = None
    qso_count = 0
    
    # Read input
    if input_file:
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    else:
        lines = sys.stdin.readlines()
    
    # Parse header fields
    qso_lines = []
    for line_num, line_raw in enumerate(lines, 1):
        # Strip leading and trailing spaces from each line
        line = line_raw.strip()
        
        if not line:
            continue
            
        if line.startswith('CALLSIGN:'):
            callsign = line.split(':', 1)[1].strip()
        elif line.startswith('GRID-LOCATOR:'):
            grid_locator = line.split(':', 1)[1].strip()
        elif line.startswith('NAME:'):
            name = line.split(':', 1)[1].strip()
        elif line.startswith('CONTEST:'):
            contest = line.split(':', 1)[1].strip()
        elif line.startswith('QSO:'):
            qso_lines.append((line_num, line))
    
    # Prepare output
    if output_file:
        out = open(output_file, 'w', encoding='utf-8')
    else:
        out = sys.stdout
    
    try:
        # Write ADIF header
        out.write("ADIF Export\n")
        out.write(f"<ADIF_VER:5>3.1.0\n")
        out.write(f"<PROGRAMID:13>cabrillo2adif\n")
        out.write(f"<PROGRAMVERSION:3>1.0\n")
        
        if callsign:
            out.write(f"<STATION_CALLSIGN:{len(callsign)}>{callsign}\n")
        if grid_locator:
            out.write(f"<MY_GRIDSQUARE:{len(grid_locator)}>{grid_locator}\n")
        if name:
            out.write(f"<MY_NAME:{len(name)}>{name}\n")
        if contest:
            out.write(f"<CONTEST_ID:{len(contest)}>{contest}\n")
        
        out.write("<EOH>\n\n")
        
        # Write QSO records
        for line_num, line in qso_lines:
            qso = parse_qso_line(line, line_num)
            if qso:
                out.write(f"<CALL:{len(qso['call'])}>{qso['call']} ")
                out.write(f"<QSO_DATE:8>{qso['date']} ")
                out.write(f"<TIME_ON:4>{qso['time']} ")
                out.write(f"<BAND:{len(get_band(qso['freq']))}>{get_band(qso['freq'])} ")
                out.write(f"<FREQ:{len(qso['freq'])}>{qso['freq']} ")
                out.write(f"<MODE:{len(qso['mode'])}>{qso['mode']} ")
                out.write(f"<RST_SENT:{len(qso['rst_sent'])}>{qso['rst_sent']} ")
                out.write(f"<RST_RCVD:{len(qso['rst_rcvd'])}>{qso['rst_rcvd']} ")
                out.write(f"<STX:{len(qso['stx'])}>{qso['stx']} ")
                out.write(f"<SRX:{len(qso['srx'])}>{qso['srx']} ")
                if callsign:
                    out.write(f"<STATION_CALLSIGN:{len(callsign)}>{callsign} ")
                if grid_locator:
                    out.write(f"<MY_GRIDSQUARE:{len(grid_locator)}>{grid_locator} ")
                if contest:
                    out.write(f"<CONTEST_ID:{len(contest)}>{contest} ")
                out.write("<EOR>\n")
                qso_count += 1
        
    finally:
        if output_file:
            out.close()

def get_band(freq_mhz):
    """Determine amateur radio band from frequency in MHz"""
    freq = float(freq_mhz)
    if 1.8 <= freq < 2.0:
        return "160m"
    elif 3.5 <= freq < 4.0:
        return "80m"
    elif 7.0 <= freq < 7.3:
        return "40m"
    elif 10.1 <= freq < 10.15:
        return "30m"
    elif 14.0 <= freq < 14.35:
        return "20m"
    elif 18.068 <= freq < 18.168:
        return "17m"
    elif 21.0 <= freq < 21.45:
        return "15m"
    elif 24.89 <= freq < 24.99:
        return "12m"
    elif 28.0 <= freq < 29.7:
        return "10m"
    elif 50.0 <= freq < 54.0:
        return "6m"
    elif 144.0 <= freq < 148.0:
        return "2m"
    elif 420.0 <= freq < 450.0:
        return "70cm"
    else:
        return "UNK"

def main():
    parser = argparse.ArgumentParser(
        description='Convert Cabrillo format logs to ADIF format'
    )
    parser.add_argument('-i', '--input', 
                       help='Input Cabrillo file (default: stdin)',
                       default=None)
    parser.add_argument('-o', '--output',
                       help='Output ADIF file (default: stdout)',
                       default=None)
    
    args = parser.parse_args()
    
    try:
        cabrillo_to_adif(args.input, args.output)
    except FileNotFoundError as e:
        sys.stderr.write(f"Error: No se encuentra el archivo {args.input}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error: {str(e)}\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
