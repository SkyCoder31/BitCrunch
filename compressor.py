import heapq
import os
import pickle
from collections import defaultdict, Counter

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

class HuffmanCoding:
    def __init__(self):
        self.heap = []
        self.codes = {}
        self.reverse_mapping = {}

    def make_frequency_dict(self, data):
        """Create frequency dictionary from byte data"""
        return Counter(data)

    def build_heap(self, frequency):
        """Build min-heap from frequency dictionary"""
        for char, freq in frequency.items():
            node = HuffmanNode(char, freq)
            heapq.heappush(self.heap, node)

    def merge_nodes(self):
        """Merge nodes to create Huffman tree"""
        while len(self.heap) > 1:
            node1 = heapq.heappop(self.heap)
            node2 = heapq.heappop(self.heap)
            merged = HuffmanNode(None, node1.freq + node2.freq)
            merged.left = node1
            merged.right = node2
            heapq.heappush(self.heap, merged)

    def make_codes_helper(self, root, current_code):
        """Helper function to generate Huffman codes"""
        if root is None:
            return
        
        # Leaf node - store the code
        if root.char is not None:
            # Handle single character case
            if not current_code:
                current_code = "0"
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return
        
        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")

    def make_codes(self):
        """Generate Huffman codes from the tree"""
        if len(self.heap) == 0:
            return
        
        root = heapq.heappop(self.heap)
        
        # Handle single character case
        if root.left is None and root.right is None:
            self.codes[root.char] = "0"
            self.reverse_mapping["0"] = root.char
        else:
            self.make_codes_helper(root, "")

    def get_encoded_text(self, data):
        """Encode data using generated Huffman codes"""
        encoded_text = ""
        for byte in data:
            encoded_text += self.codes[byte]
        return encoded_text

    def pad_encoded_text(self, encoded_text):
        """Pad encoded text to make it multiple of 8 bits"""
        extra_padding = 8 - len(encoded_text) % 8
        if extra_padding != 8:  # Only pad if needed
            encoded_text += "0" * extra_padding
        
        # Store padding info in first 8 bits
        padded_info = "{0:08b}".format(extra_padding % 8)
        encoded_text = padded_info + encoded_text
        return encoded_text

    def get_byte_array(self, padded_encoded_text):
        """Convert padded encoded text to byte array"""
        b = bytearray()
        for i in range(0, len(padded_encoded_text), 8):
            byte = padded_encoded_text[i:i+8]
            b.append(int(byte, 2))
        return b

    def compress(self, input_path, output_path):
        """Compress a file using Huffman coding"""
        with open(input_path, 'rb') as file:
            data = file.read()
        
        if len(data) == 0:
            # Handle empty file
            with open(output_path, 'wb') as output:
                output.write(b'')
            return
        
        # Create frequency dictionary
        frequency = self.make_frequency_dict(data)
        
        # Build Huffman tree
        self.build_heap(frequency)
        self.merge_nodes()
        self.make_codes()

        # Encode the data
        encoded_text = self.get_encoded_text(data)
        padded_encoded_text = self.pad_encoded_text(encoded_text)
        
        # Convert to bytes
        encoded_bytes = self.get_byte_array(padded_encoded_text)
        
        # Save compressed file
        with open(output_path, 'wb') as output:
            # Save the frequency dictionary and encoded data
            # Using pickle for reliable serialization
            header_data = {
                'frequency': frequency,
                'encoded_length': len(encoded_text)
            }
            header_bytes = pickle.dumps(header_data)
            
            # Write header length, then header, then compressed data
            output.write(len(header_bytes).to_bytes(4, byteorder='big'))
            output.write(header_bytes)
            output.write(encoded_bytes)

    def remove_padding(self, padded_encoded_text):
        """Remove padding from encoded text"""
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        
        if extra_padding == 0:
            return padded_encoded_text[8:]
        else:
            return padded_encoded_text[8:-extra_padding]

    def decode_text(self, encoded_text):
        """Decode text using Huffman codes"""
        current_code = ""
        decoded_data = bytearray()
        
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                decoded_data.append(self.reverse_mapping[current_code])
                current_code = ""
        
        return decoded_data

    def decompress(self, input_path, output_path):
        """Decompress a file compressed with Huffman Coding"""
        with open(input_path, 'rb') as file:
            # Read header length
            header_length_bytes = file.read(4)
            if len(header_length_bytes) != 4:
                # Handle empty file
                with open(output_path, 'wb') as output:
                    output.write(b'')
                return
            
            header_length = int.from_bytes(header_length_bytes, byteorder='big')
            
            # Read and deserialize header
            header_bytes = file.read(header_length)
            header_data = pickle.loads(header_bytes)
            
            frequency = header_data['frequency']
            original_encoded_length = header_data['encoded_length']
            
            # Rebuild Huffman tree
            self.build_heap(frequency)
            self.merge_nodes()
            self.make_codes()
            
            # Read compressed data
            compressed_data = file.read()
            
            # Convert back to binary string
            binary_string = ''.join(f'{byte:08b}' for byte in compressed_data)
            
            # Remove padding
            encoded_text = self.remove_padding(binary_string)
            
            # Decode
            decoded_data = self.decode_text(encoded_text)
            
            # Write decompressed data
            with open(output_path, 'wb') as output:
                output.write(decoded_data)


# Example usage:
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 4:
        print("Usage: python huffman.py [compress|decompress] <input_file> <output_file>")
        sys.exit(1)
    
    mode = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    
    h = HuffmanCoding()
    
    try:
        if mode == "compress":
            h.compress(input_file, output_file)
            print(f"File compressed successfully: {input_file} -> {output_file}")
        elif mode == "decompress":
            h.decompress(input_file, output_file)
            print(f"File decompressed successfully: {input_file} -> {output_file}")
        else:
            print("Invalid mode. Use 'compress' or 'decompress'")
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)