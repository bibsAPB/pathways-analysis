from models import Gene, Sample, SampleCollection

# TODO method for creating samples faster


def test_gene_init():
    gene = Gene('BAD')
    assert gene.name == 'BAD'

    same = Gene('BAD')
    assert same == gene
    assert same is gene

    g = Gene('TP53', 'Tumour suppressor p53')
    assert g.name == 'TP53'
    assert g.description == 'Tumour suppressor p53'

    from copy import copy
    assert copy(g).id is g.id


def test_sample_init():
    genes = {Gene('BAD'): 1.2345, Gene('FUCA2'): 6.5432}

    sample = Sample('Tumour_1', genes)

    assert sample.name == 'Tumour_1'
    assert all(isinstance(k, Gene) for k in sample.data.keys())
    assert sample.data == genes


def test_sample_from_names():
    data = {'BAD': 1.2345, 'FUCA2': 6.5432}

    sample = Sample.from_names('Tumour_1', data)

    assert sample.name == 'Tumour_1'
    assert all(isinstance(k, Gene) for k in sample.data.keys())
    assert [k.name for k in sample.data.keys()] == ['BAD', 'FUCA2']
    assert all(isinstance(v, float) for v in sample.data.values())
    assert list(sample.data.values()) == [1.2345, 6.5432]


def test_sample_collection_init():
    genes1 = {Gene('BAD'): 1.2345, Gene('FUCA2'): 6.5432}
    genes2 = {Gene('BAD'): 2.3456, Gene('FUCA2'): 7.6543}

    samples = [Sample('Tumour_1', genes1), Sample('Tumour_2', genes2)]

    sample_collection = SampleCollection('Tumour', samples)

    assert sample_collection.name == 'Tumour'
    assert all(isinstance(k, Sample) for k in sample_collection.samples)

# TODO test rest of sample_collection methods
