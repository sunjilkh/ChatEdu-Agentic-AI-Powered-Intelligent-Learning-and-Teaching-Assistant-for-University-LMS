# CO Description for FYDP-Phase-I

| CO | CO Descriptions | PO |
|----|-----------------|-----|
| CO1 | Integrate recently gained and previously acquired knowledge to identify a Retrieval-Augmented Generation (RAG) Approach for Multilingual Educational Chatbot problem for the Final Year Design Project (FYDP). | PO1 |
| CO2 | Analyze different aspects of the goals in designing a solution for mixed-language (English & Bangla) document processing and voice-enabled educational systems for the FYDP. | PO2 |
| CO3 | Explore diverse problem domains through a literature review, delineate the issues related to multilingual NLP and educational AI, and establish the goals for the FYDP. | PO4 |
| CO4 | Perform economic evaluation and cost estimation using open-source technologies and employ suitable project management procedures throughout the development life cycle of the FYDP. | PO11 |

## Project Overview:

### Introduction

Education in the digital age requires intelligent systems that can understand and process multiple languages seamlessly. In Bangladesh and other multilingual societies, students and educators often work with documents in both English and Bangla, creating a significant challenge for traditional document processing systems. Current educational technologies primarily focus on English content, leaving a substantial gap in supporting native language learning and mixed-language educational materials.

The rise of Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG) systems has revolutionized how we interact with documents and knowledge bases. However, most existing systems lack proper support for Bangla language processing, voice input capabilities, and the ability to handle mixed-language content effectively. This creates barriers for educators and students who need to work with multilingual educational materials, particularly in academic settings where both English and Bangla content are prevalent.

Furthermore, the integration of voice input capabilities for multilingual content remains a significant challenge. While voice recognition systems exist for major languages, the combination of accurate Bangla speech recognition with intelligent document retrieval and generation has not been adequately addressed in current educational technology solutions.

### Background

Recent advances in artificial intelligence and large language models (LLMs) have transformed educational technology landscapes globally. Alkhatlan and Kalita [1] observe that intelligent tutoring systems have evolved significantly, but most focus on single-language implementations. Tang et al. [3] point out that modern AI educational tools often work in isolation, lacking comprehensive integration of multiple capabilities.

The challenge becomes more pronounced in multilingual educational environments. Kumar Bhowmick et al. [4] report success in automatic question generation using transformers, but their work primarily focuses on English content. Kurdi et al. [5] reviewed 93 papers on automatic question generation and found that incorporating additional knowledge sources improves question quality, but multilingual support remains limited.

In the context of document processing and retrieval systems, current solutions face several limitations:

1. **Language Barrier**: Most RAG systems are optimized for English, with limited support for Bangla or mixed-language content.
2. **Voice Integration**: While voice recognition exists, combining it with multilingual document retrieval remains challenging.
3. **Educational Focus**: Generic chatbots lack the specialized features needed for educational content interaction.
4. **Cost Barriers**: Many advanced systems require expensive API calls or cloud services, limiting accessibility in educational institutions.

The Bangladeshi educational system, like many multilingual societies, requires solutions that can seamlessly handle both English and Bangla content. Students often encounter textbooks, research papers, and educational materials in both languages, necessitating a system that can process, understand, and respond to queries across language boundaries.

Recent developments in open-source LLMs (particularly through Ollama), advanced embedding models (including BanglaBERT), and voice recognition technologies (such as Whisper and BanglaSpeech2Text) have created new opportunities to address these challenges without relying on expensive proprietary solutions.

## Objectives:

1. **Primary Objective**: Develop a comprehensive Retrieval-Augmented Generation (RAG) system capable of processing mixed-language (English & Bangla) educational documents with voice input capabilities.

2. **Secondary Objectives**:
   - Implement advanced multilingual text processing using BanglaBERT for Bangla and Nomic Embed for English content
   - Integrate voice input processing with both Whisper and BanglaSpeech2Text for accurate multilingual speech recognition
   - Achieve sub-7 second response times through performance optimization techniques
   - Maintain high accuracy rates (>80% success rate) for both English and Bangla queries
   - Provide precise page-level citations for educational content verification
   - Create a user-friendly interface supporting both text and voice interactions

3. **Technical Objectives**:
   - Develop language-aware document chunking and processing
   - Implement intelligent caching mechanisms for improved performance
   - Create comprehensive testing frameworks for multilingual evaluation
   - Ensure system scalability and maintainability through modular architecture

## Methodology/ Requirement Specification:

### Research Design/ Prototype Design

Our research follows a systematic approach to developing a multilingual RAG system optimized for educational content. The design philosophy centers on creating a modular, scalable system that can handle the complexities of mixed-language processing while maintaining high performance and accuracy.

**System Architecture Design:**
The system employs a multi-layered architecture consisting of:
1. **Document Processing Layer**: Handles PDF loading, language detection, and intelligent chunking
2. **Embedding Layer**: Utilizes specialized models (BanglaBERT for Bangla, Nomic Embed for English)
3. **Vector Database Layer**: ChromaDB for efficient similarity search and retrieval
4. **Language Processing Layer**: Ollama-hosted LLMs (qwen2:1.5b, phi3) for generation
5. **Voice Processing Layer**: Whisper and BanglaSpeech2Text for speech recognition
6. **Interface Layer**: Command-line and voice interfaces for user interaction

**Performance Optimization Strategy:**
- Singleton pattern implementation for model caching
- Database connection pooling and persistent caching
- Smart translation pipeline with language detection
- Prompt optimization to reduce token usage by 74%
- Threading for concurrent processing

### Data Collection/ Need Assessment

**Dataset Characteristics:**
- Primary educational content: "Cormen - Introduction to Algorithms" (5.5MB PDF)
- 3,335 document chunks processed and indexed
- Mixed-language content support (English primary, Bangla secondary)
- Page-level metadata preservation for accurate citations

**Technical Requirements Assessment:**
1. **Hardware Requirements**: Local processing capabilities with GPU acceleration support
2. **Software Dependencies**: 53 optimized Python packages including langchain, transformers, torch
3. **Model Requirements**: Ollama models (qwen2:1.5b, nomic-embed-text, phi3)
4. **Voice Processing**: PyAudio, Whisper, BanglaSpeech2Text integration

**User Need Analysis:**
- Support for both text and voice queries
- Accurate page-level citations
- Sub-7 second response times
- Mixed-language query processing
- Educational content-specific optimizations

### Analysis Techniques

**Language Processing Analysis:**
- Automatic language detection using langdetect
- Specialized embedding generation based on detected language
- Context-aware prompt generation for improved accuracy

**Performance Analysis Methodology:**
- Comprehensive test suites with 23 mixed-language test cases
- Response time measurement and optimization
- Success rate calculation across languages
- Confidence level assessment for generated responses

**Quality Assurance Techniques:**
- Ablation studies comparing different model configurations
- Cross-language validation testing
- Citation accuracy verification
- User experience evaluation through interactive sessions

## Progress Achieved:

### Completed Tasks

**1. Core System Development:**
- ✅ **Document Processing Pipeline**: Implemented complete PDF loading, chunking, and indexing system
- ✅ **Multilingual Embedding System**: Integrated BanglaBERT and Nomic Embed with automatic language detection
- ✅ **Vector Database Setup**: ChromaDB implementation with persistent storage and 3,335 indexed documents
- ✅ **LLM Integration**: Ollama-hosted models with intelligent fallback mechanisms

**2. Performance Optimization:**
- ✅ **Response Time Optimization**: Achieved 83.2% improvement (36.11s → 6.06s)
- ✅ **Caching Implementation**: Model and database caching with 20-30% hit rates
- ✅ **Prompt Optimization**: 74% token reduction (2,688 → 691 characters)
- ✅ **Smart Translation Pipeline**: Eliminated unnecessary translations for English queries

**3. Voice Integration:**
- ✅ **Whisper Integration**: Multilingual speech recognition implementation
- ✅ **BanglaSpeech2Text**: Enhanced Bangla speech recognition with multiple model sizes
- ✅ **Voice Interface**: Interactive voice sessions with real-time processing
- ✅ **Audio Processing**: Complete pipeline from recording to text conversion

**4. Testing and Quality Assurance:**
- ✅ **Comprehensive Test Suite**: 23 mixed-language test cases implemented
- ✅ **Performance Benchmarking**: Multiple test iterations with detailed metrics
- ✅ **Quality Metrics**: Success rate tracking and confidence assessment
- ✅ **Automated Testing**: Full system validation with minimal human intervention

**5. Documentation and Organization:**
- ✅ **Project Streamlining**: Organized structure with 30% file reduction
- ✅ **Comprehensive Documentation**: README, technical specs, and user guides
- ✅ **Test Reports**: Organized historical test results and analysis
- ✅ **Research Documentation**: Paper drafts and evaluation metrics

### Results Obtained

**Performance Metrics (Latest - August 6, 2025):**
- **Overall Success Rate**: 82.61% (19/23 tests passed)
- **English Success Rate**: 75.0% (9/12 tests) - Target for improvement
- **Bangla Success Rate**: 90.91% (10/11 tests) - Excellent performance
- **Average Response Time**: 6.06 seconds (83.2% faster than initial)
- **High Confidence Responses**: 82.6% of all responses
- **Page Citation Accuracy**: 100% proper source attribution

**Technical Achievements:**
- **Speed Improvement**: 5.96x faster than pre-optimization system
- **Cache Efficiency**: 20-30% hit rate reducing database query overhead
- **Model Loading**: Instant response after initial warm-up through singleton pattern
- **Token Efficiency**: 74% reduction in prompt size improving processing speed

**System Capabilities Demonstrated:**
- Seamless mixed-language query processing
- Accurate page-level citations with book names
- Voice input processing in both English and Bangla
- Real-time response generation with educational content focus
- Robust error handling and system monitoring

## Challenges Faced:

| S.No. | Issues and Challenges | Strategies or Plans |
|-------|----------------------|-------------------|
| 1 | **Language Detection Accuracy**: Initial language detection was inconsistent, particularly for mixed-language queries and short text inputs, leading to incorrect embedding model selection. | Implemented multi-stage language detection with confidence thresholds. Added fallback mechanisms and manual language specification options. Enhanced detection with context-aware analysis and technical term recognition. |
| 2 | **Voice Recognition for Bangla**: Whisper frequently misidentified Bangla speech as other languages (especially Greek), resulting in poor transcription quality for Bangla voice inputs. | Integrated BanglaSpeech2Text as the primary Bangla ASR system with Whisper as fallback. Implemented language-specific model routing and confidence-based selection. Added manual language forcing options for better accuracy. |
| 3 | **Response Time Optimization**: Initial system response times averaged 36+ seconds, making it impractical for interactive use in educational settings. | Implemented comprehensive optimization strategy including model caching, database connection pooling, prompt optimization, and smart translation pipeline. Achieved 83.2% improvement in response times. |
| 4 | **English Query Success Rate**: English queries showed lower success rates (75%) compared to Bangla (90.91%), indicating system bias toward Bangla processing despite English being the primary content language. | Developed English-specific enhancements including technical term preprocessing, enhanced retrieval algorithms, optimized prompt templates, and increased retrieval chunk counts for English queries. |
| 5 | **System Complexity and Organization**: The project grew complex with multiple launcher files, scattered documentation, and redundant demo scripts, making maintenance and deployment challenging. | Conducted comprehensive project streamlining: consolidated launchers into single entry point (main.py), organized all documentation in Test Reports/ structure, and removed redundant files achieving 30% reduction in root directory clutter. |

## Next Steps:

| S.No. | Next Task | Estimate completion time (MM-YY) |
|-------|-----------|--------------------------------|
| 1 | **English Success Rate Improvement**: Implement advanced English query processing techniques to achieve 80%+ success rate, including enhanced prompt engineering and retrieval optimization. | SEP-25 |
| 2 | **Advanced Voice Features**: Develop real-time voice processing, noise cancellation, and improved mixed-language speech recognition capabilities. | OCT-25 |
| 3 | **Web Interface Development**: Create a comprehensive web-based interface using Gradio or FastAPI for broader accessibility and deployment. | NOV-25 |
| 4 | **Multi-Document Support**: Extend system to handle multiple PDF documents simultaneously with cross-document query capabilities. | DEC-25 |
| 5 | **Research Paper Completion**: Finalize the academic paper "Explainable Textbook Chatbots: Verifiable Page-Level Citation in a Bangla RAG System" with comprehensive evaluation and publication submission. | JAN-26 |

## Updated Timeline:

| Tasks | Weeks | | | | | | | | | | | | | | | | | |
|-------|-------|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| | 24 | 25 | 26 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 | 39 | 40 | 41 |
| English Success Rate Improvement | ████ | ████ | ████ | ████ | | | | | | | | | | | | | | |
| Advanced Voice Features | | | ████ | ████ | ████ | ████ | | | | | | | | | | | | |
| Web Interface Development | | | | | ████ | ████ | ████ | ████ | | | | | | | | | | |
| Multi-Document Support | | | | | | | ████ | ████ | ████ | ████ | | | | | | | | |
| Research Paper Completion | | | | | | | | | ████ | ████ | ████ | ████ | ████ | ████ | | | | |

**Estimated Work Period**: 24 weeks (September 2025 - February 2026)
**Actual Work Period**: [To be updated as tasks progress]

## Resources Utilized:

**Software and Libraries:**
- **Core Framework**: Python 3.8+ with 53 optimized dependencies
- **LLM Integration**: Ollama (qwen2:1.5b, phi3, nomic-embed-text models)
- **Language Processing**: LangChain, transformers, BanglaBERT, sentence-transformers
- **Vector Database**: ChromaDB with persistent storage
- **Voice Processing**: OpenAI Whisper, BanglaSpeech2Text, PyAudio
- **Development Tools**: Google Colab, VS Code, Git version control

**Hardware Resources:**
- **Development Environment**: Local workstation with GPU acceleration support
- **Storage**: 5.5MB+ document corpus with 3,335 indexed chunks
- **Memory**: Optimized for efficient model caching and database operations

**Educational Content:**
- **Primary Dataset**: "Cormen - Introduction to Algorithms" textbook
- **Language Coverage**: English primary content with Bangla query support
- **Metadata**: Complete page-level indexing for accurate citations

**Cloud and Deployment:**
- **Development Platform**: Google Colab for experimentation and testing
- **Version Control**: Git repository with comprehensive change tracking
- **Documentation**: Organized test reports and technical documentation

## Project Management and Financial Analysis:

### Table 3.1: Estimated Cost for BanglaRAG Project

| SN | Components | Estimated Cost (BDT) |
|----|------------|---------------------|
| 01. | Development Tools and Software | 0 (Open Source) |
| 02. | Hardware and Computing Resources | 15,000-25,000 |
| 03. | Internet and Cloud Services | 2,000-3,000 |
| 04. | Educational Content and Datasets | 0 (Open Access) |
| 05. | Testing and Validation | 1,000-2,000 |
| 06. | Documentation and Report Writing | 2,000-3,000 |
| 07. | Contingency (10% of total) | 2,000-3,300 |
| **Total Estimated Cost** | | **22,000-36,300** |

**Cost Optimization Benefits:**
- **Open Source Approach**: Eliminated licensing costs for LLMs and development tools
- **Local Processing**: Reduced cloud API expenses through local model hosting
- **Efficient Architecture**: Minimized computational requirements through optimization

## Future Considerations:

**Technical Scalability:**
- Potential computational limitations for larger document corpora
- Memory optimization requirements for expanded model support
- Database scaling considerations for multi-user environments

**Educational Integration:**
- Learning Management System (LMS) integration requirements
- Compliance with educational data privacy standards
- Accessibility features for diverse user needs

**Research and Development:**
- Advanced multilingual model fine-tuning opportunities
- Integration with emerging Bengali NLP research
- Contribution to open-source educational AI community

**Deployment Challenges:**
- Institutional infrastructure compatibility
- User training and adoption strategies
- Maintenance and update procedures for production environments

## Conclusion:

This progress report demonstrates the successful development of a comprehensive multilingual RAG system specifically designed for educational applications. The BanglaRAG system has achieved significant milestones in addressing the critical gap in multilingual educational technology, particularly for English-Bangla mixed-language processing.

**Key Achievements:**
- **Performance Excellence**: 83.2% improvement in response times with 82.61% overall success rate
- **Multilingual Capability**: Superior Bangla processing (90.91% success) with ongoing English optimization (75% success)
- **Voice Integration**: Comprehensive speech recognition supporting both languages
- **Educational Focus**: Page-level citations and academic content optimization
- **Open Source Approach**: Cost-effective solution using entirely open-source technologies

**Technical Innovations:**
- Advanced language-aware document processing
- Intelligent model caching and optimization strategies  
- Comprehensive voice input integration with multiple ASR systems
- Streamlined architecture with professional organization

**Research Contributions:**
The project addresses critical research questions in multilingual educational AI, particularly in the underserved area of Bangla-English mixed-language processing. The system's focus on explainable citations and educational content makes it a valuable contribution to the academic community.

**Future Impact:**
The BanglaRAG system demonstrates the feasibility of developing sophisticated multilingual educational AI systems using open-source technologies. This approach makes advanced educational AI accessible to institutions and researchers with limited budgets, potentially democratizing access to intelligent tutoring technologies in multilingual educational environments.

The next phase will focus on further optimization, web interface development, and comprehensive academic publication to share these innovations with the broader research community.

## References

[1] A. Alkhatlan and J. Kalita, "Intelligent Tutoring Systems: A Comprehensive Historical Survey with Recent Developments," arXiv preprint arXiv:1812.09628, Dec. 2018.

[2] J. Roldán-Álvarez, "Intelligent Deep-Learning Tutoring System to Assist Instructors in Programming Courses," IEEE Trans. Educ., early access, 2023.

[3] Q. Tang et al., "Agent4EDU: Advancing AI for Education with Agentic Workflows," IEEE Trans. Learn. Technol., early access, 2025.

[4] A. Kumar Bhowmick et al., "Automating Question Generation from Educational Text," arXiv preprint arXiv:2309.15004, Sep. 2023.

[5] G. Kurdi et al., "A Systematic Review of Automatic Question Generation for Educational Purposes," Int. J. Artif. Intell. Educ., vol. 30, no. 1, pp. 121–204, 2019.

[6] R. Gao et al., "Automatic Assessment of Text-Based Responses in Post-Secondary Education: A Systematic Review," arXiv preprint arXiv:2308.16151, Aug. 2023.

[7] L. Yan et al., "Practical and Ethical Challenges of Large Language Models in Education: A Systematic Scoping Review," PLoS One, vol. 18, no. 4, Apr. 2023.

[8] D. Azizov et al., "Advancing AI for Education with Agentic Workflows," Springer, 2025.

[9] Invidious Community, "Invidious API," [Online]. Available: https://invidious.snopyta.org (accessed May 2025).

[10] D. Santandreu Calonge et al., "AI Agents and Agentic Systems: A Multi-Expert Analysis," Elsevier Educ. Inf. Technol., vol. 30, no. 2, pp. 3575–3598, 2025.

[11] F. Kamalov et al., "Evolution of AI in Education: Agentic Workflows," IEEE Frontiers Comput. Sci., 2025.

[12] Z. Chu et al., "LLM Agents for Education: Advances and Applications," Springer Frontiers Comput. Sci., 2025.

[13] Ollama Team, "Ollama: Get up and running with large language models locally," [Online]. Available: https://ollama.ai/ (accessed Aug. 2025).

[14] S. Sarker et al., "BanglaBERT: Language Model Pretraining and Benchmarks for Low-Resource Language Understanding Evaluation in Bangla," in Findings of EMNLP, 2021.

[15] OpenAI, "Whisper: Robust Speech Recognition via Large-Scale Weak Supervision," arXiv preprint arXiv:2212.04356, 2022.

[16] S. H. Hossain, "BanglaSpeech2Text: Open Source Bengali Speech Recognition," GitHub repository, 2024. [Online]. Available: https://github.com/shhossain/BanglaSpeech2Text

[17] ChromaDB Team, "Chroma: The open-source embedding database," [Online]. Available: https://www.trychroma.com/ (accessed Aug. 2025).