import marshal
import os
import pickle
import sys
from array import array
from typing import Dict
from typing import Tuple

#given sequence of bytes, creates dictionary of occurrences per byte
def calcFrequencies(message: bytes):
    frequencies = {}

    for i in range(len(message)):
        if message[i] not in frequencies:
            frequencies[message[i]] = 1
        else:
            frequencies[message[i]] +=1
            
    return frequencies


#######INVARIANT FOR TREE CALCULATION#######

#Invariant: This invariant seeks to convert an array of (byte, frequency) tuples
#into a huffman tree that will be useful for calculating huffman codes for compression

#Initialization: At the start of the invariant, the function is given the entire (byte, freq) array
#which is then sorted by frequency.

#Maintenance: Progress is being made when the front 2 tuples of the array are converted into a
#tuple pair of an array of the original 2 tuples and the combined frequency of the 2 original tuples.
#The original 2 tuples are removed and the new combined tuple is appended to the array, decreasing the
#length of the array by 1 each iteration. At the start of each loop iteration the array is then resorted
#by frequency to ensure that the next front 2 tuples contain the lowest 2 frequencies in the array.

#Termination: The invariant ends when the length of the tuple array is 1. This means that every tuple has been
#combined and we are left with a tuple that represents the huffman tree.

#given a frequency dictionary, calcs tree
def calcTree(freqTable):
    sortedFreqs = sorted(freqTable, key=lambda tup: tup[1])

    #runs until freqTable is 1 large data struct that represents the entire tree
    while len(sortedFreqs) > 1:
        #sort by frequency then combine 2 front elements(lowest 2 branches)
        sortedFreqs = sorted(sortedFreqs, key=lambda tup: tup[1])
        newFreq = ([sortedFreqs[0] ,sortedFreqs[1]],sortedFreqs[0][1] + sortedFreqs[1][1])
        sortedFreqs.pop(0)
        sortedFreqs.pop(0)
        sortedFreqs.append(newFreq)

    sortedFreqs = sorted(sortedFreqs, key=lambda tup: tup[1])
    
    return sortedFreqs


#recursively traverse the tree to create a codeBook
def codeBookMaker(tree, code, codeBook):

    #base case is the type passed in is an int(byte value)
    if type(tree) == int:
        #create dict entry w/ byte value and code which was recursively passed in
        bitStr = ""
        codeBook[tree] = bitStr.join(code)
        return codeBook

    #recursively traverse left/right of tree, using code parameter to track tree path
    codeBookMaker(tree[0][0], code + ['1'], codeBook)
    codeBookMaker(tree[1][0], code + ['0'], codeBook)
    return codeBook


    
def encode(message: bytes) -> Tuple[str, Dict]:
    """ Given the bytes read from a file, encodes the contents using the Huffman encoding algorithm.

    :param message: raw sequence of bytes from a file
    :returns: string of 1s and 0s representing the encoded message
              dict containing the decoder ring as explained in lecture and handout.
    """  

    #generate freqTable, tree then codeBook using the message parameter
    frequencies = calcFrequencies(message)
    freqTable = frequencies.items()
    tree = calcTree(freqTable)
    codeBook = codeBookMaker(tree[0][0], [], {})
    encodedMessage = ""
   
    for i in range(len(message)):
        encodedMessage+= codeBook.get(message[i])

    #invert codebook dict for convenience in decompressing before return
    flippedCodeBook = {v: k for k, v in codeBook.items()}
    
              
    return (encodedMessage, flippedCodeBook)



#######INVARIANT FOR DECODING#######

#Invariant: This invariant seeks to convert a string of bits into a byte array to be read to disk
#given a decoder ring

#Initialization: At the start of the invariant, both the array of bytes and the variable
#to track the current code being evaluated are empty.

#Maintenance: Progress is being made when the for loop iterates through the message parameter, adding the current bit
#to a variable to track the code as a string. After the current bit is appended to the string, the dictionary is
#searched to check if that tracker variable represents a valid code in the dictionary. If so, the byte value of
#that code is appended to the byte array and the tracker variable to reset to an empty string.

#Termination: The invariant ends when the for loop terminates, which means every bit from the message parameter
#has been read and the byte array is complete.
def decode(message: str, decoder_ring: Dict) -> bytes:
    """ Given the encoded string and the decoder ring, decodes the message using the Huffman decoding algorithm.

    :param message: string of 1s and 0s representing the encoded message
    :param decoder_ring: dict containing the decoder ring
    return: raw sequence of bytes that represent a decoded file
    """
    currentCode = ""
    byte_array = array('B')

    #append 1 bit at a time from message and check if it is a valid code in codebook
    for i in range(len(message)):
        currentCode+=(message[i])

        #if valid code, append value to byte_array and reset currentCode        
        if currentCode in decoder_ring:
            byte_array.append(decoder_ring.get(currentCode))
            currentCode = ""
            
    return byte_array


def compress(message: bytes) -> Tuple[array, Dict]:
    """ Given the bytes read from a file, calls encode and turns the string into an array of bytes to be written to disk.

    :param message: raw sequence of bytes from a file
    :returns: array of bytes to be written to disk
              dict containing the decoder ring
    """
    encodedMessage, codeBook = encode(message)
    byte_array = array('B')
    byteStr = ""

    #calc num of full bytes in encodedMessage and append 1 byte at a time to byte array
    numFullBytes = int(len(encodedMessage) / 8)
    for i in range(numFullBytes):
        byte_array.append(int(encodedMessage[i * 8: (i * 8) + 8], 2))
            
        
    lastByte = (encodedMessage[8 * numFullBytes:])
    #create flag byte(2nd to last) to indicate how much padding the last byte has
    byte_array.append(8 - len(encodedMessage[8 * numFullBytes:]))
    

    #if needed, pads 0's to the front of the last byte until its a full byte
    while(len(lastByte) != 8):
        lastByte+='0'
    
    byte_array.append(int(lastByte, 2))
    
    return (byte_array, codeBook)
    

def decompress(message: array, decoder_ring: Dict) -> bytes:
    """ Given a decoder ring and an array of bytes read from a compressed file, turns the array into a string and calls decode.

    :param message: array of bytes read in from a compressed file
    :param decoder_ring: dict containing the decoder ring
    :return: raw sequence of bytes that represent a decompressed file
    """

    #check flag byte (2nd to last) to see how many bits in last byte were packed and unpack
    numPadding = message[len(message)- 2]
    paddedByte = "{:08b}".format(int(message[len(message) - 1]))
    unpaddedByte = (paddedByte[: 8 - numPadding])
    byteStr = ""
   
    #append everything up to flag byte
    for i in range(len(message) - 2):   
        binaryByte = "{:08b}".format(int(message[i]))
        byteStr+=binaryByte

        
    byteStr+=unpaddedByte  

    return decode(byteStr, decoder_ring)


if __name__ == '__main__':
    usage = f'Usage: {sys.argv[0]} [ -c | -d | -v | -w ] infile outfile'
    if len(sys.argv) != 4:
        raise Exception(usage)

    operation = sys.argv[1]
    if operation not in {'-c', '-d', '-v', 'w'}:
        raise Exception(usage)

    infile, outfile = sys.argv[2], sys.argv[3]
    if not os.path.exists(infile):
        raise FileExistsError(f'{infile} does not exist.')

    if operation in {'-c', '-v'}:
        with open(infile, 'rb') as fp:
            _message = fp.read()

        if operation == '-c':
            _message, _decoder_ring = compress(_message)
            with open(outfile, 'wb') as fp:
                marshal.dump((pickle.dumps(_decoder_ring), _message), fp)
        else:
            _message, _decoder_ring = encode(_message)
            print(_message)
            with open(outfile, 'wb') as fp:
                marshal.dump((pickle.dumps(_decoder_ring), _message), fp)

    else:
        with open(infile, 'rb') as fp:
            pickleRick, _message = marshal.load(fp)
            _decoder_ring = pickle.loads(pickleRick)

        if operation == '-d':
            bytes_message = decompress(array('B', _message), _decoder_ring)
        else:
            bytes_message = decode(_message, _decoder_ring)
        with open(outfile, 'wb') as fp:
            fp.write(bytes_message)
    
