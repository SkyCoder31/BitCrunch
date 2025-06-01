import heapq
import os
from collections import defaultdict

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

    def make_frequency_dict(self, text):
        # For binary data, count frequency of each 8-bit chunk
        frequency = {}
        for i in range(0, len(text), 8):
            chunk = text[i:i+8]
            if chunk not in frequency:
                frequency[chunk] = 0
            frequency[chunk] += 1
        
        # For DOC files, add common patterns with weights
        if hasattr(self, 'input_path') and self.input_path.lower().endswith('.doc'):
            doc_patterns = {
                '10101010': 1000,  # Common alternating pattern
                '11111111': 1000,  # Common all-ones pattern
                '00000000': 1000,  # Common all-zeros pattern
                '01010101': 1000,  # Common alternating pattern
            }
            # Update frequency dictionary with weighted patterns
            for pattern, weight in doc_patterns.items():
                if pattern in frequency:
                    frequency[pattern] += weight
                else:
                    frequency[pattern] = weight
        
        return frequency

    def encode_text(self, text):
        # For binary data, encode each 8-bit chunk
        encoded_text = ""
        for i in range(0, len(text), 8):
            chunk = text[i:i+8]
            if chunk in self.codes:
                encoded_text += self.codes[chunk]
        return encoded_text

    def decode_text(self, encoded_text):
        current_code = ""
        decoded_text = ""
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                decoded_text += self.reverse_mapping[current_code]
                current_code = ""
        return decoded_text

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
        if root.char is not None:
            self.codes[root.char] = current_code
            self.reverse_mapping[current_code] = root.char
            return
        self.make_codes_helper(root.left, current_code + "0")
        self.make_codes_helper(root.right, current_code + "1")

    def make_codes(self):
        """Generate Huffman codes from the tree"""
        root = heapq.heappop(self.heap)
        current_code = ""
        self.make_codes_helper(root, current_code)

    def get_encoded_text(self, text):
        """Encode text using generated Huffman codes"""
        encoded_text = ""
        # Process 8 bits at a time
        for i in range(0, len(text), 8):
            byte = text[i:i+8]
            if byte in self.codes:
                encoded_text += self.codes[byte]
        return encoded_text

    def pad_encoded_text(self, encoded_text):
        """Pad encoded text to make it multiple of 8 bits"""
        extra_padding = 8 - len(encoded_text) % 8
        for i in range(extra_padding):
            encoded_text += "0"
        padded_info = "{0:08b}".format(extra_padding)
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
        # Read file as binary for PDF and DOCX files
        with open(input_path, 'rb') as file, open(output_path, 'wb') as output:
            # Read binary data
            binary_data = file.read()
            
            # Preprocess DOC files for better compression
            if input_path.lower().endswith('.doc'):
                # DOC files have repeating patterns - find common sequences
                sequences = self.find_common_sequences(binary_data)
                # Replace common sequences with shorter markers
                binary_data = self.replace_common_sequences(binary_data, sequences)
            
            # Convert binary data to string of bits
            text = ''.join(f'{byte:08b}' for byte in binary_data)
            
            # Create frequency dictionary for 8-bit chunks
            frequency = self.make_frequency_dict(text)
            
            # For DOC files, add common patterns to frequency dictionary
            if input_path.lower().endswith('.doc'):
                # Add common DOC file patterns
                doc_patterns = {
                    '10101010': 1000,  # Common alternating pattern
                    '11111111': 1000,  # Common all-ones pattern
                    '00000000': 1000,  # Common all-zeros pattern
                    '01010101': 1000,  # Common alternating pattern
                }
                # Update frequency dictionary with weighted patterns
                for pattern, weight in doc_patterns.items():
                    if pattern in frequency:
                        frequency[pattern] += weight
                    else:
                        frequency[pattern] = weight
            
            self.build_heap(frequency)
            self.merge_nodes()
            self.make_codes()

            # Compress the binary data
            encoded_text = self.get_encoded_text(text)
            padded_encoded_text = self.pad_encoded_text(encoded_text)
            
            # Save header with frequency information
            header = f"{len(frequency)}\n"
            for char, freq in frequency.items():
                header += f"{char} {freq}\n"
            
            # For DOC files, add special header
            if input_path.lower().endswith('.doc'):
                header += "DOC_FILE\n"
            
            # Write header
            output.write(header.encode('utf-8'))
            
            # Write compressed data
            b = self.get_byte_array(padded_encoded_text)
            output.write(bytes(b))

    def decompress(self, input_path, output_path):
        with open(input_path, 'rb') as file, open(output_path, 'wb') as output:
            # Read header
            header = b''
            while True:
                char = file.read(1)
                if char == b'\n':
                    break
                header += char
            
            # Get frequency count
            freq_count = int(header.decode('utf-8'))
            
            # Read frequency dictionary
            frequency = {}
            for _ in range(freq_count):
                char = b''
                while True:
                    byte = file.read(1)
                    if byte == b'\n':
                        break
                    char += byte
                freq = int(file.read(1))
                frequency[char.decode('utf-8')] = freq
            
            # Check if this is a DOC file
            is_doc = False
            if file.read(9) == b'DOC_FILE\n':
                is_doc = True
            
            # Build Huffman tree
            self.build_heap(frequency)
            self.merge_nodes()
            self.make_codes()
            
            # Read compressed data
            compressed_data = file.read()
            
            # Convert to binary string
            binary_string = ''.join(f'{byte:08b}' for byte in compressed_data)
            
            # Remove padding
            padding_info = binary_string[:8]
            extra_padding = int(padding_info, 2)
            binary_string = binary_string[8:-extra_padding]
            
            # Decode using Huffman codes
            decoded_text = self.remove_padding(self.decode_text(binary_string))
            
            # Convert back to bytes
            decoded_bytes = bytearray()
            for i in range(0, len(decoded_text), 8):
                byte = int(decoded_text[i:i+8], 2)
                decoded_bytes.append(byte)
            
            # For DOC files, restore common sequences
            if is_doc:
                decoded_bytes = self.restore_common_sequences(decoded_bytes)
            
            # Write to output file
            output.write(decoded_bytes)

    def find_common_sequences(self, data: bytes) -> dict:
        """Find common sequences in DOC files"""
        sequences = {}
        # Check for common DOC patterns
        patterns = [
            b'\x00\x00\x00\x00',  # Common null pattern
            b'\xFF\xFF\xFF\xFF',  # Common all-ones pattern
            b'\xAA\xAA\xAA\xAA',  # Common alternating pattern
            b'\x55\x55\x55\x55',  # Common alternating pattern
        ]
        
        for pattern in patterns:
            count = data.count(pattern)
            if count > 10:  # Only consider patterns that appear multiple times
                sequences[pattern] = count
        
        return sequences

    def replace_common_sequences(self, data: bytes, sequences: dict) -> bytes:
        """Replace common sequences with shorter markers"""
        result = bytearray()
        marker = b'\xFF'  # Use FF as marker since it's rare in DOC files
        
        i = 0
        while i < len(data):
            found = False
            for seq, count in sequences.items():
                if data[i:i+len(seq)] == seq:
                    # Write marker followed by sequence index
                    result.extend(marker)
                    result.append(count % 256)  # Store count in one byte
                    i += len(seq)
                    found = True
                    break
            if not found:
                result.append(data[i])
                i += 1
        
        return bytes(result)

    def restore_common_sequences(self, data: bytes) -> bytes:
        """Restore common sequences from markers"""
        result = bytearray()
        marker = b'\xFF'
        
        i = 0
        while i < len(data):
            if data[i:i+1] == marker:
                # Read sequence index
                seq_index = data[i+1]
                # Restore sequence
                result.extend(self.common_sequences[seq_index])
                i += 2
            else:
                result.append(data[i])
                i += 1
        
        return bytes(result)

    def decompress(self, input_path, output_path):
        with open(input_path, 'rb') as file, open(output_path, 'wb') as output:
            # Read header
            header = b''
            while True:
                char = file.read(1)
                if char == b'\n':
                    break
                header += char
            
            # Get frequency count
            freq_count = int(header.decode('utf-8'))
            
            # Read frequency dictionary
            frequency = {}
            for _ in range(freq_count):
                char = b''
                while True:
                    byte = file.read(1)
                    if byte == b'\n':
                        break
                    char += byte
                freq = int(file.read(1))
                frequency[char.decode('utf-8')] = freq
            
            # Build Huffman tree
            self.build_heap(frequency)
            self.merge_nodes()
            self.make_codes()
            
            # Read compressed data
            compressed_data = file.read()
            
            # Convert to binary string
            binary_string = ''.join(f'{byte:08b}' for byte in compressed_data)
            
            # Remove padding
            padding_info = binary_string[:8]
            extra_padding = int(padding_info, 2)
            binary_string = binary_string[8:-extra_padding]
            
            # Decode using Huffman codes
            decoded_text = self.remove_padding(self.decode_text(binary_string))
            
            # Convert back to bytes
            decoded_bytes = bytearray()
            for i in range(0, len(decoded_text), 8):
                byte = int(decoded_text[i:i+8], 2)
                decoded_bytes.append(byte)
            
            # Write to output file
            output.write(decoded_bytes)

    def remove_padding(self, padded_encoded_text):
        """Remove padding from encoded text"""
        padded_info = padded_encoded_text[:8]
        extra_padding = int(padded_info, 2)
        padded_encoded_text = padded_encoded_text[8:] 
        encoded_text = padded_encoded_text[:-1*extra_padding]
        return encoded_text

    def decode_text(self, encoded_text):
        """Decode text using Huffman codes"""
        current_code = ""
        decoded_text = ""
        for bit in encoded_text:
            current_code += bit
            if current_code in self.reverse_mapping:
                character = self.reverse_mapping[current_code]
                decoded_text += character
                current_code = ""
        return decoded_text

    def decompress(self, input_path, output_path):
        """Decompress a file compressed with Huffman Coding"""
        with open(input_path, 'rb') as file, open(output_path, 'w') as output:
            # Read header information
            header = b''
            while True:
                byte = file.read(1)
                if byte == b'\n':
                    break
                header += byte
            
            # Parse header
            header = header.decode('utf-8')
            num_chars = int(header.split('\n')[0])
            
            # Build frequency dictionary from header
            frequency = {}
            for _ in range(num_chars):
                char_info = file.readline().decode('utf-8').strip()
                if char_info:
                    char, freq = char_info.split()
                    frequency[char] = int(freq)
            
            # Rebuild Huffman tree
            self.build_heap(frequency)
            self.merge_nodes()
            self.make_codes()
            
            # Read and decode compressed data
            compressed_data = file.read()
            bit_string = ''
            for byte in compressed_data:
                byte = bin(byte)[2:].rjust(8, '0')
                bit_string += byte
            
            encoded_text = self.remove_padding(bit_string)
            decompressed_text = self.decode_text(encoded_text)
            
            output.write(decompressed_text)

# Example usage:
if __name__ == "__main__":
    import sys
    import tempfile
    import shutil
    import os
    
    if len(sys.argv) != 4:
        print("Usage: python huffman.py compress <input_file> <output_file>")
        sys.exit(1)
    
    mode = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Copy input file to temp directory
            temp_input = os.path.join(temp_dir, os.path.basename(input_file))
            shutil.copy2(input_file, temp_input)
            
            h = HuffmanCoding()
            
            if mode == "compress":
                # Create temp output file
                temp_output = os.path.join(temp_dir, os.path.basename(output_file))
                h.compress(temp_input, temp_output)
                # Copy compressed file back
                shutil.copy2(temp_output, output_file)
            elif mode == "decompress":
                # Create temp output file
                temp_output = os.path.join(temp_dir, os.path.basename(output_file))
                h.decompress(temp_input, temp_output)
                # Copy decompressed file back
                shutil.copy2(temp_output, output_file)
            else:
                print("Invalid mode. Use 'compress' or 'decompress'")
                sys.exit(1)
        except Exception as e:
            print(f"Error processing file: {e}")
            sys.exit(1)
        finally:
            # Clean up temp directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"Warning: Failed to clean up temp directory: {e}")
