import os
import re
import sys
import json

###
# Global variables
###
sourceType = ''
source = ''
destination = '.'

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

    if sourceType == 'file':
        sourceFile = open(source)
        files = []
        for line in sourceFile:
            match = re.search(r'[_0-9a-zA-Z]+.[a-zA-Z]+', line)
            files.append(match.group().lower())
        return files

def writeMetadata(metadata):
    '''
    Writes the metadata that has been parsed into a file. Searches the
    working directory for existing metadata files and avoid conflict using
    an incrementing suffix
    '''
    global destination

    base = 'image_file_metadata'
    augment = ''
    pattern = base + r'(\([0-9]+\))?\.json'

    matches = []
    makeNext = 0

    # Find existing metadata files
    for filename in os.listdir(destination):
        match = re.search(pattern, filename)
        if match:
            matches.append(match.group())

    # If there are existing metadata files, get the increment
    #   value for the new one
    if len(matches) > 0:
        makeNext = 1
    for filename in matches:
        match = re.search(r'[0-9]+', filename)
        if match:
            value = int(match.group())
            if value >= makeNext:
                makeNext = value + 1
    if makeNext > 0:
        augment = '(' + str(makeNext) + ')'

    # Open the file and write the metadata
    metadataFile = open(base+augment+'.json', 'w')
    json.dump(metadata, metadataFile)

def trimUnderscores(name):
    ''' 
    Removes underscores from the beginning and end of name
    '''
    # Chop off the leading underscored
    for i, letter in enumerate(name):
        if letter != '_':
            name = name[i:]
            break
    # Chop off the trailing underscores
    for i, letter in enumerate(reversed(name)):
        if letter != '_':
            name = name[:len(name)-i]
            break
    return name
    # Working on a snazzy regex solution
    #match = re.search(r'(?<=_|^)[_a-z0-9](?=_|$)', name);

def getAndRemoveProcess(name):
    '''
    Find the process information for tif files. Currently assumes a
    specific set of valid processes, and assumes that the process info
    will be found at the beginning of the file name
    '''
    processTypes = ['v_reg', 'reg', 'mask_nuclei', 'v_nuclei']

    # Check for each possible process type (currently simplified for task)
    for process in processTypes:
        # Search the beginning of the file name for the process
        regexString = '^' + process
        match = re.search(regexString, name)
        # If a match is found, remove the process from the name and return
        if match:
            nameWithoutProcess = name[match.end()+1:]
            return trimUnderscores(nameWithoutProcess), match.group()
    else:
        return name, 'NA'


def getAndRemoveROI(name):
    '''
    Find the ROI from the file name, remove if from the file name
    and return. Assumes that the ROI is found at the end of the 
    file name.
    ***SENSITIVE TO OUT-OF-ORDER METADATA COMPONENTS***
    '''
    match = re.search(r'roi[0-9]+$', name)
    if match:
        roi = match.group()
        nameWithoutROI = trimUnderscores(name[:match.start()])
        return nameWithoutROI, roi[3:]
    else:
        return name, 'NA'

def getAndRemoveMarker(name):
    '''
    Find the optional marker from the file name, remove if and return.
    Assumes that the marker is the portion of the file after the last underscore.
    Current order of execution assumptions are that this will be run 
    after getAndRemoveROI and before getAndRemoveCycleRound.
    ***SENSITIVE TO OUT-OF-ORDER METADATA COMPONENTS***
    '''
    match = re.search(r'(?<=_)[0-9a-z]+$', name)
    if match:
        marker = match.group()
        nameWithoutMarker = trimUnderscores(name[:match.start()])
        return nameWithoutMarker, marker
    else:
        return name, 'NA'

def getAndRemoveCycleRound(name):
    '''
    Find the cycle and round values from the file name, removes them
    and returns. Currently assumes that they are the last component
    of the file name, and that this function is run after both
    getAndRemoveROI and getAndRemoveMarker.
    ***SENSITIVE TO OUT-OF-ORDER METADATA COMPONENTS***
    '''
    match = re.search(r'c[0-9]+r[0-9]+$', name)
    if match:
        # Remove the cycle and round from the name
        nameWithoutCycleRound = trimUnderscores(name[:match.start()])
        # Extract the cycle and round info from the regex match and return
        parts = match.group().split('r')
        return nameWithoutCycleRound, parts[0][1:], parts[1]

    else:
        return name, 'NA', 'NA'

def getAndRemoveStudy(name):
    ''' 
    Find the study information from the file name. Currently assumes
    that any preceeding information in the file name has been parsed
    for importand metadata, and discards the rest. 
    *** SENSITIVE TO UNORDERED METADATA***
    '''
    # 
    match = re.search(r'[a-z]+_?[0-9]+$', name)
    if match:
        nameWithoutStudy = trimUnderscores(name[:match.start()])
        study = match.group()
        if '_' not in study:
            for i, letter in enumerate(study):
                if letter.isdigit():
                    study = study[:i] + '_' + study[i:]
                    break
        return nameWithoutStudy, study
    else:
        return name, 'NA'

def processFilenames(names):
    fileMetadata = []

    # Iterate through the filenames and
    for imageID, file in enumerate(names):
        # Separate the file name and file extension
        parts = file.split('.')
        extension = re.search(r'[a-z0-9]+', parts[1]).group()
        name = parts[0]
        leftover = name
        #print(name)
        #print('Image type: {}'.format(extension))
       
        # If the file is a tif, get the process
        if extension == 'tif':
            leftover, process = getAndRemoveProcess(leftover)
        else:
            process = 'NA'
        #print('Process: {}'.format(process))

        # Get the ROI
        leftover, roi = getAndRemoveROI(leftover)
        #print('ROI: {}'.format(roi))
        
        # Get the marker
        leftover, marker = getAndRemoveMarker(leftover)
        #print('Marker: {}'.format(marker))

        # Get the cycle and round numbers
        leftover, cycle, round = getAndRemoveCycleRound(leftover)
        #print('Cycle: {} - Round: {}'.format(cycle, round))

        # Get the Study
        leftover, study = getAndRemoveStudy(leftover)
        #print('Study: {}'.format(study))

        print('Leftover: {}'.format(leftover))
        #print('\n')

        fileMetadata.append({'image_id': imageID,
                             'filename': file,
                             'cycle': cycle, 
                             'round': round,
                             'marker': marker,
                             'region': roi,
                             'image_type': extension,
                             'study': study, 
                             'process': process})
        print(fileMetadata[-1])

    return fileMetadata
        

if __name__ == '__main__':
    processArgs()
    filenames = getFileNames()
    metadata = processFilenames(filenames)
    writeMetadata(metadata)
    

