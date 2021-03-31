
# Huffman-Encoding


This is an algorithm that I implemented for one of my college algorithm courses that I found very interesting.

Huffman coding provides a way to implement lossless data compression by first creating a table that records the frequency
of bytes(0-255). Using this frequency table, you can recursively create a codebook for each byte by first creating a tree representation
where the two smallest frequency nodes are paired until a single node is left. Recursively traversing this tree, you can assign bits to the left and right paths; whenever a byte node is reached, the code which represents the path traversed through the tree will be that bytes code for compression. The goal of this algorithm is to assign bit codes that contain fewer bits to bytes that occur more frequently which allows for more space efficient compression.


# Diagram representing codebook creation for a small frequency table
![Capture](https://user-images.githubusercontent.com/79820503/113082565-b872da00-91a8-11eb-9c36-263757c989fe.PNG)


# Try it for yourself!

-Download or clone my repository

To compress, enter: 
```
$ python huffman.py -c example.txt example.huf
```


To decompress enter: <code>$ python huffman.py -d example.huf example.txt</code>


This lossless compression program can reduce the size of .txt files by approximately half! :)
