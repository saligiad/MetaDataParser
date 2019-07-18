import os
import re
import sys
import json

###
# Global variables
###
sourceType = ''
source = ''
destination = ''
filenames = []
metadata = []

def processArgs():
    '''
    Process the command line arguments to the script
    '''
    global sourceType
    global source

    sourceType = 'file'
    source = 'Python_Task_Files.txt'

def getFileNames():
    '''
    Determine the source of file names and retrieve the names
    '''
    global sourceType
    global source
    global filenames

    if sourceType == 'file':
        sourceFile = open(source)
        filenames = [line.lower() for line in sourceFile]

def getAndRemoveCycleRound(parts):
    for i, part in enumerate(parts):
        match = re.search(r'c[0-9]+r[0-9]+', part)
        if match:
            parts.pop(i)
            cycleAndRound = match.group(0).split('r')
            return cycleAndRound[0][1:], cycleAndRound[1]
    return 'NA', 'NA'

def getAndRemoveROI(parts):
    for i, part in enumerate(parts):
        match = re.search(r'roi[0-1]+', part)
        if match:
            parts.pop(i)
            return match.group(0)[3:]
    return 'NA'

def getAndRemoveStudy(parts):
    for i, part in enumerate(parts):
        # Match if the study is across two name parts
        match = re.search(r'^[0-9]+', part)
        if match:
            ret = parts[i-1] + '_' + parts[i]
            parts.pop(i)
            parts.pop(i-1)
            return ret
        # Match if the study is contained in one part
        match = re.search(r'(?<!c[0-9][0-9]r)[0-9]+', part)
        if match:
            changeIndex = 0
            for i, letter in enumerate(parts[i]):
                if letter.isdigit():
                    changeIndex = i
                    break
            ret = parts[i][:changeIndex] + '-' + parts[i][changeIndex]
            parts.pop(i)
            return ret
    return 'NA'

def processFilenames(names):
    for file in filenames:
        # Get the file extension
        parts = file.split('.')
        extension = parts[1]

        components = parts[0].split('_')
        
        # Get the cycle and round numbers
        cycle, round = getAndRemoveCycleRound(components)
        print('Cycle: {} - Round: {}'.format(cycle, round))

        # Get the ROI
        roi = getAndRemoveROI(components)
        print('ROI: {}'.format(roi))

        # Get the Study
        study = getAndRemoveStudy(components)
        print('Study: {}\n'.format(study))



if __name__ == '__main__':
    processArgs()
    getFileNames()
    processFilenames(filenames)

