import re
from . import vvFunctions as fn


class Variant(object):
    """
    This Variant object will contain the original input, the processed variant description and any other data that's
    relevant to what kind of variant it is.
    """

    def __init__(self, original, quibble=None, warnings='', write=True, primary_assembly=False, order=False):
        self.original = original
        if quibble is None:
            self.quibble = original
        else:
            self.quibble = quibble
        self.hgvs_formatted = None
        self.hgvs_genomic = None
        self.hgvs_coding = None
        self.stashed = None
        self.pre_RNA_conversion = None
        self.input_parses = None

        self.warnings = warnings
        self.description = ''  # hgnc_gene_info variable
        self.coding = ''
        self.coding_g = ''
        self.genomic_r = ''
        self.genomic_g = ''
        self.protein = ''
        self.write = write
        self.primary_assembly = primary_assembly
        self.order = order
        self.output_type_flag = 'warning'

        self.test_stash_tx_left = None
        self.test_stash_tx_right = None

        self.timing = {}

        self.refsource = None
        self.reftype = None

        self.hn = None
        self.reverse_normalizer = None
        self.evm = None
        self.no_norm_evm = None
        self.min_evm = None
        self.lose_vm = None

        self.gene_symbol = None
        self.hgvs_transcript_variant = None
        self.genome_context_intronic_sequence = None
        self.refseqgene_context_intronic_sequence = None
        self.hgvs_refseqgene_variant = None
        self.hgvs_predicted_protein_consequence = None
        self.validation_warnings = None
        self.hgvs_lrg_transcript_variant = None
        self.hgvs_lrg_variant = None
        self.alt_genomic_loci = None
        self.primary_assembly_loci = None
        self.reference_sequence_records = None
        self.validated = False

    def is_ascii(self):
        """
        Instead of the previous test for unicode rich text characters.
        Now going to test that all characters are within the ascii alphabet
        """
        try:
            self.quibble.encode('ascii')
            return True
        except UnicodeEncodeError or UnicodeDecodeError:
            # Will catch errors raised by python 2 and python 3
            return False

    def get_non_ascii(self):
        """
        Will return non ascii character positions within variant description
        :return:
        """
        chars = []
        positions = []

        for i, c in enumerate(self.quibble):
            try:
                c.encode('ascii')
            except UnicodeEncodeError or UnicodeDecodeError:
                chars.append(c)
                positions.append(i+1)

        return chars, positions

    def remove_whitespace(self):
        """
        Will remove all whitespace from quibble
        :return:
        """
        self.quibble = ''.join(self.quibble.split())

    def format_quibble(self):
        """
        Removes whitespace from the ends of the string
        Removes anything in brackets
        Identifies variant type (p. c. etc)
        Accepts c, g, n, r currently. And now P also 15.07.15
        """
        # Set regular expressions for if statements
        pat_gene = re.compile(r'\(.+?\)')  # Pattern looks for (....)

        if pat_gene.search(self.quibble):
            self.quibble = pat_gene.sub('', self.quibble)

        try:
            self.set_refsource()
        except fn.VariantValidatorError:
            return True

        try:
            self.set_reftype()
        except fn.VariantValidatorError:
            return True

        return False

    def set_reftype(self):
        """
        Method will set the reftype based on the quibble
        :return:
        """
        pat_est = re.compile(r'\d\:\d')

        if ':g.' in self.quibble:
            self.reftype = ':g.'
        elif ':r.' in self.quibble:
            self.reftype = ':r.'
        elif ':n.' in self.quibble:
            self.reftype = ':n.'
        elif ':c.' in self.quibble:
            self.reftype = ':c.'
        elif ':p.' in self.quibble:
            self.reftype = ':p.'
        elif ':m.' in self.quibble:
            self.reftype = ':m.'
        elif pat_est.search(self.quibble):
            self.reftype = 'est'
        else:
            raise fn.VariantValidatorError("Unable to identity reference type from %s" % self.quibble)

    def set_refsource(self):
        """
        Method will set the refsource based on the quibble
        :return:
        """
        if self.quibble.startswith('LRG'):
            self.refsource = 'LRG'
        elif self.quibble.startswith('ENS'):
            self.refsource = 'ENS'
        elif self.quibble.startswith('N'):
            self.refsource = 'RefSeq'
        else:
            raise fn.VariantValidatorError("Unable to identify reference source from %s" % self.quibble)

    def set_quibble(self, newval):
        """
        Method will set the quibble and reset the refsource and reftype
        :param newval:
        :return:
        """
        self.quibble = newval
        self.set_refsource()
        self.set_reftype()

    def output_dict(self):
        """
        Method will return the output values as a dictionary
        :return: dict
        """
        dict_out = {
            'submitted_variant': self.original,
            'gene_symbol': self.gene_symbol,
            'transcript_description': self.description,
            'hgvs_transcript_variant': self.hgvs_transcript_variant,
            'genome_context_intronic_sequence': self.genome_context_intronic_sequence,
            'refseqgene_context_intronic_sequence': self.refseqgene_context_intronic_sequence,
            'hgvs_refseqgene_variant': self.hgvs_refseqgene_variant,
            'hgvs_predicted_protein_consequence': self.hgvs_predicted_protein_consequence,
            'validation_warnings': self.validation_warnings,
            'hgvs_lrg_transcript_variant': self.hgvs_lrg_transcript_variant,
            'hgvs_lrg_variant': self.hgvs_lrg_variant,
            'alt_genomic_loci': self.alt_genomic_loci,
            'primary_assembly_loci': self.primary_assembly_loci,
            'reference_sequence_records': self.reference_sequence_records,
        }
        return dict_out

    def is_obsolete(self):
        """
        Checks whether the keyword 'obsolete' appears within the validation warnings
        :return:
        """
        return any('obsolete' in warning for warning in self.validation_warnings)