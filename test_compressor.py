import unittest
import tempfile
import os
import pickle # For testing invalid pickle data
from compressor import HuffmanCoding, HuffmanNode # Assuming compressor.py is in the same directory

class TestHuffmanCoding(unittest.TestCase):

    def setUp(self):
        self.huffman_coder = HuffmanCoding()
        # Create temporary file names for use in tests
        # These will be created and deleted within each test method that needs them
        self.input_file_path = None
        self.compressed_file_path = None
        self.decompressed_file_path = None

    def tearDown(self):
        # Ensure cleanup of any files that might have been left due to errors
        for path in [self.input_file_path, self.compressed_file_path, self.decompressed_file_path]:
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass # Ignore if somehow already deleted or permission issue

    def _write_to_temp_file(self, data_bytes):
        # Helper to create and write to a named temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(data_bytes)
        temp_file.close()
        return temp_file.name

    def test_make_frequency_dict(self):
        self.assertEqual(self.huffman_coder.make_frequency_dict(b""), {})
        freq_dict = self.huffman_coder.make_frequency_dict(b"aabbc")
        self.assertEqual(freq_dict, {ord('a'): 2, ord('b'): 2, ord('c'): 1})
        freq_dict_unique = self.huffman_coder.make_frequency_dict(b"abc")
        self.assertEqual(freq_dict_unique, {ord('a'): 1, ord('b'): 1, ord('c'): 1})

    def test_build_heap(self):
        freq_dict = {ord('a'): 2, ord('b'): 2, ord('c'): 1}
        self.huffman_coder.build_heap(freq_dict)
        self.assertEqual(len(self.huffman_coder.heap), 3)
        sorted_heap = sorted(self.huffman_coder.heap, key=lambda x: x.freq)
        self.assertEqual(sorted_heap[0].freq, 1)
        self.assertEqual(sorted_heap[0].char, ord('c'))
        self.huffman_coder.heap = []
        self.huffman_coder.build_heap({})
        self.assertEqual(len(self.huffman_coder.heap), 0)

    def test_make_codes_single_char(self):
        freq_dict_single = {ord('a'): 5}
        self.huffman_coder.build_heap(freq_dict_single)
        self.huffman_coder.merge_nodes()
        self.huffman_coder.make_codes()
        self.assertEqual(self.huffman_coder.codes, {ord('a'): "0"})
        self.huffman_coder.heap = []
        self.huffman_coder.codes = {}
        self.huffman_coder.reverse_mapping = {}
        self.huffman_coder.make_codes()
        self.assertEqual(self.huffman_coder.codes, {})

    def test_make_codes_simple(self):
        freq_dict = {ord('a'): 3, ord('b'): 2, ord('c'): 1}
        self.huffman_coder.build_heap(freq_dict)
        self.huffman_coder.merge_nodes()
        self.huffman_coder.make_codes()
        codes = self.huffman_coder.codes
        self.assertEqual(len(codes[ord('a')]), 1)
        self.assertTrue(len(codes[ord('b')]) >= len(codes[ord('a')]))
        self.assertTrue(len(codes[ord('c')]) >= len(codes[ord('b')]))
        self.assertEqual(len(set(codes.values())), 3)
        self.assertEqual(set(codes.keys()), {ord('a'), ord('b'), ord('c')})

    def test_get_encoded_text(self):
        self.huffman_coder.codes = {ord('a'): "0", ord('b'): "10", ord('c'): "11"}
        encoded_text = self.huffman_coder.get_encoded_text(b"abc")
        self.assertEqual(encoded_text, "01011")
        encoded_text_empty = self.huffman_coder.get_encoded_text(b"")
        self.assertEqual(encoded_text_empty, "")

    def test_pad_encoded_text(self):
        padded_text = self.huffman_coder.pad_encoded_text("10101")
        self.assertEqual(padded_text, "0000001110101000")
        padded_text_no_pad = self.huffman_coder.pad_encoded_text("10101010")
        self.assertEqual(padded_text_no_pad, "0000000010101010")
        padded_text_empty = self.huffman_coder.pad_encoded_text("")
        self.assertEqual(padded_text_empty, "00000000")

    def test_remove_padding(self):
        removed_padding_text = self.huffman_coder.remove_padding("0000001110101000")
        self.assertEqual(removed_padding_text, "10101")
        removed_padding_text_no_pad = self.huffman_coder.remove_padding("0000000010101010")
        self.assertEqual(removed_padding_text_no_pad, "10101010")
        removed_padding_empty = self.huffman_coder.remove_padding("00000000")
        self.assertEqual(removed_padding_empty, "")

    def test_decode_text(self):
        self.huffman_coder.reverse_mapping = {"0": ord('a'), "10": ord('b'), "11": ord('c')}
        decoded_bytes = self.huffman_coder.decode_text("01011")
        self.assertEqual(decoded_bytes, bytearray(b"abc"))
        decoded_bytes_empty = self.huffman_coder.decode_text("")
        self.assertEqual(decoded_bytes_empty, bytearray(b""))

    # End-to-end tests
    def _test_compress_decompress_cycle(self, data_bytes):
        self.input_file_path = self._write_to_temp_file(data_bytes)
        self.compressed_file_path = tempfile.NamedTemporaryFile(delete=False).name
        self.decompressed_file_path = tempfile.NamedTemporaryFile(delete=False).name

        try:
            # Reset coder state for each cycle if methods are stateful beyond passed args
            self.huffman_coder = HuffmanCoding()
            self.huffman_coder.compress(self.input_file_path, self.compressed_file_path)

            # For empty file, specific check for compressed size if defined by implementation
            if not data_bytes:
                 self.assertEqual(os.path.getsize(self.compressed_file_path), 0, "Compressed empty file should be 0 bytes")

            # Reset coder state for decompression
            self.huffman_coder = HuffmanCoding()
            self.huffman_coder.decompress(self.compressed_file_path, self.decompressed_file_path)

            with open(self.decompressed_file_path, 'rb') as f:
                decompressed_content = f.read()
            self.assertEqual(decompressed_content, data_bytes)
        finally:
            for path in [self.input_file_path, self.compressed_file_path, self.decompressed_file_path]:
                if path and os.path.exists(path):
                    os.remove(path)
            self.input_file_path, self.compressed_file_path, self.decompressed_file_path = None, None, None


    def test_compress_decompress_empty_file(self):
        self._test_compress_decompress_cycle(b"")

    def test_compress_decompress_single_char_file(self):
        self._test_compress_decompress_cycle(b"aaaaa")

    def test_compress_decompress_simple_file(self):
        self._test_compress_decompress_cycle(b"aabbc")

    def test_compress_decompress_longer_file(self):
        self._test_compress_decompress_cycle(b"This is a test string for Huffman coding.")

    def test_decompress_invalid_file_not_pickle(self):
        self.input_file_path = self._write_to_temp_file(b"This is not a pickle header at all, just some random bytes.")
        self.decompressed_file_path = tempfile.NamedTemporaryFile(delete=False).name

        try:
            self.huffman_coder = HuffmanCoding()
            # The current decompress reads 4 bytes for header length first.
            # If these 4 bytes are e.g. b"This", it will be a large number.
            # Then it tries to read that many bytes for the header.
            # If the file is short, it will be an EOFError or similar during file.read(header_length).
            # If the file is long enough but the data isn't pickle, it will be pickle.UnpicklingError.
            with self.assertRaises((pickle.UnpicklingError, EOFError, ValueError)): # ValueError if header_length_bytes is not valid int bytes
                 self.huffman_coder.decompress(self.input_file_path, self.decompressed_file_path)
        finally:
            if self.input_file_path and os.path.exists(self.input_file_path):
                os.remove(self.input_file_path)
            if self.decompressed_file_path and os.path.exists(self.decompressed_file_path):
                os.remove(self.decompressed_file_path)
            self.input_file_path, self.decompressed_file_path = None, None


    def test_decompress_incomplete_header(self):
        # Header length: 100 bytes, but only 10 bytes of actual header data
        header_length_bytes = (100).to_bytes(4, byteorder='big')
        incomplete_header_data = header_length_bytes + b"short head" # 4 + 10 = 14 bytes

        self.input_file_path = self._write_to_temp_file(incomplete_header_data)
        self.decompressed_file_path = tempfile.NamedTemporaryFile(delete=False).name

        try:
            self.huffman_coder = HuffmanCoding()
            # Expecting pickle.UnpicklingError because it tries to load an incomplete pickle string,
            # or EOFError if the file.read(header_length) itself causes it before pickle.loads
            with self.assertRaises((pickle.UnpicklingError, EOFError)):
                self.huffman_coder.decompress(self.input_file_path, self.decompressed_file_path)
        finally:
            if self.input_file_path and os.path.exists(self.input_file_path):
                os.remove(self.input_file_path)
            if self.decompressed_file_path and os.path.exists(self.decompressed_file_path):
                os.remove(self.decompressed_file_path)
            self.input_file_path, self.decompressed_file_path = None, None

if __name__ == '__main__':
    unittest.main()
