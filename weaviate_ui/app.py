import os
import traceback
import streamlit as st
import weaviate
from weaviate.client import WeaviateClient
from weaviate.classes.init import Auth
from weaviate.classes.query import Filter
import itertools
import random
from collections import Counter
from typing import List, Iterable

HYBRID_SEARCH_ALPHA = float(os.getenv("HYBRID_SEARCH_ALPHA", "0.25"))

def get_weaviate_client(host: str, port: int, user_key: str) -> WeaviateClient:
    client = weaviate.connect_to_local(
        host=host,
        port=port,
        auth_credentials=Auth.api_key(user_key)
    )
    if not client.is_live():
        raise ConnectionError("Can't connect to an instance of weaviate database")
    return client

def sample_combinations(keywords: List[str], max_samples: int = 10, seed: int | None = None) -> Iterable[str]:
    """
    Yield a limited number of non-empty keyword combinations.
    """
    if not keywords:
        return

    all_combos = []
    for r in range(1, len(keywords) + 1):
        all_combos.extend(" ".join(combo) for combo in itertools.combinations(keywords, r))

    total = len(all_combos)
    if total == 0:
        return

    n_to_yield = min(total, max_samples)
    rng = random.Random(seed)
    chosen = rng.sample(all_combos, n_to_yield)

    for combo in chosen:
        yield combo

def convert_weaviate_objects_to_display(weaviate_objects):
    """Convert Weaviate objects to a displayable format"""
    documents = []
    for obj in weaviate_objects:
        source = obj.properties.get('source', 'Unknown source')
        doc = {
            'content': obj.properties.get('content', ''),
            'metadata': {k: v for k, v in obj.properties.items() if k not in ['content', 'source']},
            'source': source,
            'uuid': str(obj.uuid),
            'score': obj.metadata.score if obj.metadata else None,
            'distance': obj.metadata.distance if obj.metadata else None
        }
        documents.append(doc)
    return documents

def main():
    st.title("Weaviate Document Search")

    # Sidebar for connection settings
    with st.sidebar:
        st.header("Connection Settings")
        host = st.text_input("Weaviate Host", value=os.getenv("WEAVIATE_HOST"))
        port = st.number_input("Port", value=int(os.getenv("WEAVIATE_PORT")))
        user_key = st.text_input("User Key", value=os.getenv("WEAVIATE_USER_KEY"), type="password")
        
        if st.button("Connect"):
            try:
                client = get_weaviate_client(host, port, user_key)
                st.session_state.client = client
                st.success("Successfully connected to Weaviate!")
                
                # Get available collections
                collections = [col for col in client.collections.list_all()]
                st.session_state.collections = collections
                
                # Get all available sources for the first collection
                if collections:
                    collection = client.collections.get(collections[0])
                    response = collection.query.fetch_objects(
                        limit=10000,
                    )
                    
                    # Store all unique sources in session state
                    all_sources = {obj.properties.get('source', 'Unknown') for obj in response.objects}
                    st.session_state.all_sources = sorted(list(all_sources))
                    
            except Exception as e:
                st.error(f"Connection failed: {str(e)}")

    # Main content
    if 'client' in st.session_state:
        # Collection selection
        if 'collections' in st.session_state:
            selected_collection = st.selectbox(
                "Select Collection",
                st.session_state.collections
            )

            # Collection Statistics Section
            st.header("Collection Statistics")
            
            # Add source filter input
            source_name = st.text_input("Filter by source name (e.g., 'document.pdf', leave empty for all sources)")
            
            if st.button("Show Collection Stats"):
                try:
                    collection = st.session_state.client.collections.get(selected_collection)
                    
                    # Get all objects to count and analyze with optional source filter
                    if source_name.strip():
                        response = collection.query.fetch_objects(
                            limit=10000,  # Adjust this based on your collection size
                            filters=Filter.by_property("source").equal(source_name.strip())
                        )
                        st.info(f"Showing statistics for source: {source_name}")
                    else:
                        response = collection.query.fetch_objects(
                            limit=10000  # Adjust this based on your collection size
                        )
                        st.info("Showing statistics for all sources")
                    
                    # Calculate total count
                    total_count = len(response.objects)
                    st.write(f"Total documents in collection: {total_count}")
                    
                    # Calculate source statistics
                    source_counts = {}
                    for obj in response.objects:
                        source = obj.properties.get('source', 'Unknown')
                        source_counts[source] = source_counts.get(source, 0) + 1
                    
                    # Store sources in session state for reuse
                    st.session_state.sources = list(source_counts.keys())
                    st.session_state.source_counts = source_counts
                    
                    # Display source statistics
                    if source_name.strip():
                        st.subheader(f"Statistics for source: {source_name}")
                    else:
                        st.subheader("Documents per Source")
                    
                    sorted_sources = sorted(st.session_state.source_counts.items(), 
                                         key=lambda x: x[1], 
                                         reverse=True)
                    
                    for source, count in sorted_sources:
                        with st.expander(f"{source} ({count} documents)"):
                            # Get sample documents for this source
                            samples = collection.query.fetch_objects(
                                limit=5,  # Get 5 samples
                                offset=0,
                                filters=Filter.by_property("source").equal(source)
                            )
                            
                            # Access the objects property of QueryReturn
                            for i, doc in enumerate(samples.objects, 1):
                                st.markdown(f"**Sample {i}:**")
                                content_preview = doc.properties.get('content', '')[:200] + '...' if len(doc.properties.get('content', '')) > 200 else doc.properties.get('content', '')
                                st.write(content_preview)
                                st.markdown("---")
                except Exception as e:
                    error = traceback.format_exc()
                    st.error(f"Failed to fetch collection statistics: {str(error)}")
            
            # Source filtering for search
            source_filter = None
            if 'all_sources' in st.session_state:
                st.subheader("Filter by Source")
                selected_source = st.selectbox(
                    "Select source to filter search results",
                    ["All Sources"] + st.session_state.all_sources
                )
                if selected_source != "All Sources":
                    source_filter = Filter.by_property("source").equal(selected_source)

            # Search interface
            st.header("Search Documents")
            query = st.text_input("Enter your search query")
            top_k = st.slider("Number of results", min_value=1, max_value=50, value=10)
            alpha = st.slider("Hybrid Search Alpha (0 for BM25, 1 for vector)", 
                            min_value=0.0, max_value=1.0, value=0.5)

            if st.button("Search"):
                try:
                    collection = st.session_state.client.collections.get(selected_collection)
                    
                    # Split query into keywords for advanced search
                    keywords = query.split(",")
                    aggregated_docs = []
                    
                    # Add keyword combinations
                    keyword_list = list(keywords)
                    for combo in sample_combinations(keywords=keyword_list, max_samples=1):
                        keyword_list.append(combo)
                    keyword_list.append(query)  # Add original query
                    
                    with st.spinner("Searching documents..."):
                        for keyword in keyword_list:
                            # Add source filter to the query if selected
                            query_params = {
                                "query": keyword.strip(),
                                "limit": top_k,
                                "alpha": HYBRID_SEARCH_ALPHA
                            }
                            if source_filter:
                                query_params["filters"] = source_filter
                            
                            response = collection.query.hybrid(**query_params)
                            docs = convert_weaviate_objects_to_display(response.objects)
                            aggregated_docs.extend(docs)
                    
                    # Get unique documents by UUID
                    unique_docs = {doc['uuid']: doc for doc in aggregated_docs}
                    documents = list(unique_docs.values())
                    
                    # Sort by score
                    documents.sort(key=lambda x: x['score'] if x['score'] is not None else 0, reverse=True)
                    
                    # Display results
                    st.header(f"Found {len(documents)} unique documents")
                    
                    for i, doc in enumerate(documents, 1):
                        score_text = f"Score: {doc['score']:.4f}" if doc['score'] is not None else "Score: N/A"
                        with st.expander(f"Document {i} from {doc['source']} ({score_text})"):
                            # Source and Score
                            st.markdown("### Source")
                            st.write(f"**Source:** {doc['source']}")
                            # st.write(f"**Score:** {doc['score']:.4f if doc['score'] is not None else 'N/A'}")
                            
                            # Content
                            st.markdown("### Content")
                            st.write(doc['content'])
                            
                            # Metadata
                            if doc['metadata']:
                                st.markdown("### Metadata")
                                for key, value in doc['metadata'].items():
                                    st.write(f"**{key}:** {value}")
                            
                            # Technical details
                            st.markdown("### Technical Details")
                            st.write(f"UUID: {doc['uuid']}")
                            if doc['distance'] is not None:
                                st.write(f"Distance: {doc['distance']:.4f}")
                            if doc['score'] is not None:
                                st.write(f"Score: {doc['score']:.4f}")
                            else:
                                st.write("Score: N/A")

                except Exception as e:
                    error = traceback.format_exc()

                    st.error(f"Search failed: {str(error)}")
        else:
            st.warning("No collections found in the database.")
    else:
        st.info("Please connect to Weaviate using the sidebar settings.")

if __name__ == "__main__":
    main()