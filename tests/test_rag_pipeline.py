import pytest

from chatbot.rag_pipeline import (
    load_documents,
    split_into_chunks,
    retrieve_relevant_chunks
)

def test_load_documents_returns_four_documents():

    documents = load_documents()

    assert len(documents) == 4


def test_loaded_documents_are_not_empty():

    documents = load_documents()

    for document in documents:
        assert document.strip() != ""


def test_loaded_documents_are_strings():

    documents = load_documents()

    for document in documents:
        assert isinstance(document, str)


from chatbot.rag_pipeline import split_into_chunks


def test_split_into_chunks_returns_chunks():

    documents = ["A" * 1000]

    chunks = split_into_chunks(documents)

    assert len(chunks) == 3


def test_chunk_size_does_not_exceed_limit():

    documents = ["A" * 1200]

    chunks = split_into_chunks(documents, chunk_size=500, overlap=50)

    for chunk in chunks:
        assert len(chunk) <= 500


def test_chunks_have_expected_overlap():

    documents = ["A" * 1000]

    chunks = split_into_chunks(documents, chunk_size=500, overlap=50)

    assert chunks[0][-50:] == chunks[1][:50]


def test_empty_document_list_returns_empty_chunks():

    chunks = split_into_chunks([])

    assert chunks == []


def test_retrieval_returns_relevant_delivery_information():

    chunks = [
        "Standard delivery takes 3 to 5 working days.",
        "Express delivery costs £7.99.",
        "Returns are accepted within 30 days."
    ]

    results = retrieve_relevant_chunks(
        "How much does express delivery cost?",
        chunks
    )

    assert "Express delivery costs £7.99." in results


def test_retrieval_returns_top_k_chunks():

    chunks = [
        "Express delivery costs £7.99.",
        "Standard delivery takes 3 to 5 days.",
        "Customers can return products within 30 days."
    ]

    results = retrieve_relevant_chunks(
        "delivery information",
        chunks,
        top_k=2
    )

    assert len(results) == 2


def test_retrieval_handles_empty_question():

    chunks = ["Express delivery costs £7.99."]

    with pytest.raises(ValueError, match="Question cannot be empty"):
        retrieve_relevant_chunks("", chunks)


def test_retrieval_handles_empty_chunks():

    results = retrieve_relevant_chunks(
        "How much does delivery cost?",
        []
    )

    assert results == []



def test_retrieval_understands_express_delivery_charge():

    documents = load_documents()
    chunks = split_into_chunks(documents)

    results = retrieve_relevant_chunks(
        "What's the express delivery charge?",
        chunks
    )

    combined_results = " ".join(results).lower()

    assert "express delivery" in combined_results
    assert "7.99" in combined_results


def test_retrieval_understands_express_shipping_paraphrase():

    documents = load_documents()
    chunks = split_into_chunks(documents)

    results = retrieve_relevant_chunks(
        "How much extra do I pay for express shipping?",
        chunks
    )

    combined_results = " ".join(results).lower()

    assert "express delivery" in combined_results
    assert "7.99" in combined_results


def test_retrieval_finds_express_delivery_time():

    documents = load_documents()
    chunks = split_into_chunks(documents)

    results = retrieve_relevant_chunks(
        "How long does express delivery take?",
        chunks
    )

    combined_results = " ".join(results).lower()

    assert "express delivery" in combined_results
    assert "1 to 2 business days" in combined_results


def test_retrieval_does_not_invent_next_day_policy():

    documents = load_documents()
    chunks = split_into_chunks(documents)

    results = retrieve_relevant_chunks(
        "Do you offer next-day delivery?",
        chunks
    )

    combined_results = " ".join(results).lower()

    assert "next-day delivery" not in combined_results

