#!/usr/bin/env python3
"""
Framework, Tool, and Pattern Detection Definitions for Claude Wrapped.

This file contains all the detection patterns for:
- Frameworks and Tools (FRAMEWORK_KEYWORDS)
- Project Components (PROJECT_COMPONENTS)
- Coding Concepts (CODING_CONCEPTS)
- Technology Patterns (TECH_PATTERNS)
- Project Categories (CATEGORY_PATTERNS)
- Display Icons (FRAMEWORK_ICONS, COMPONENT_ICONS, CONCEPT_ICONS)

Based on research from Stack Overflow Developer Survey 2025, AI framework comparisons,
and vector database market analysis.

Sources:
- Stack Overflow Developer Survey 2025: https://survey.stackoverflow.co/2025/technology
- AI Agent Frameworks Comparison: https://www.turing.com/resources/ai-agent-frameworks
- Vector Database Comparison: https://www.datacamp.com/blog/the-top-5-vector-databases
- Cloud Deployment Platforms: https://northflank.com/blog/best-cloud-app-deployment-platforms
"""

# =============================================================================
# FRAMEWORK AND TOOL KEYWORDS
# =============================================================================
# Each key is a framework/tool name, value is a list of detection keywords
# Keywords are matched case-insensitively

FRAMEWORK_KEYWORDS = {
    # =========================================================================
    # AI/LLM AGENT FRAMEWORKS
    # =========================================================================
    'claude-flow': [
        'claude-flow', '@anthropics/claude-flow', 'npm install claude-flow',
        'npx claude-flow', 'yarn add claude-flow', 'pnpm add claude-flow',
        '"claude-flow"', "'claude-flow'", 'flow.yaml', 'flow.yml',
        'claude-flow init', 'claude-flow run', 'claude-flow generate',
        'claudeflow', 'claude_flow', 'using claude-flow', 'with claude-flow',
    ],
    # SPARC detection reduced - only match explicit usage
    'sparc': [
        'sparc methodology', 'sparc framework', 'sparc workflow',
    ],
    'langgraph': [
        'langgraph', 'lang graph', 'langchain graph', 'stategraph',
        'from langgraph', 'langgraph.graph', 'graph-based agent',
    ],
    'langchain': [
        'langchain', 'lcel', 'langsmith', 'langserve',
        'from langchain', 'langchain_core', 'langchain_community',
    ],
    'crewai': [
        'crewai', 'crew.ai', 'agent crew', 'from crewai',
        'crew = crew', 'crew.kickoff', '@crew',
    ],
    'autogen': [
        'autogen', 'pyautogen', 'autogen studio', 'from autogen',
        'autogen.agentchat', 'conversableagent', 'assistantagent',
    ],
    'openai-swarm': [
        'openai swarm', 'swarm.run', 'from swarm', 'openai/swarm',
    ],
    'openai-agents-sdk': [
        'openai agents sdk', 'agents sdk', '@openai/agents',
        'openai.agents', 'agentruntime',
    ],
    'llamaindex': [
        'llamaindex', 'llama_index', 'llama-index', 'from llama_index',
    ],
    'dspy': [
        'dspy', 'from dspy', 'dspy.signature', 'dspy.module',
    ],
    'semantic-kernel': [
        'semantic kernel', 'semantic_kernel', 'from semantic_kernel',
        'microsoft.semantickernel',
    ],
    'haystack': [
        'haystack', 'from haystack', 'deepset', 'haystack-ai',
    ],
    'mcp': [
        'mcp server', 'model context protocol', 'mcp-', '@mcp/',
        'mcpservers', 'mcp tool', 'mcp integration', 'mcp.json',
        'modelcontextprotocol',
    ],
    'coscientist': [
        'coscientist', 'co-scientist', 'scientific workflow',
        'hypothesis generation', 'experiment design', 'literature review',
    ],
    'agentic-engineering': [
        '@agent-', 'agent-devops', 'agent-frontend', 'agent-backend',
        'agentic-engineering', 'ciign', 'multi-agent', 'agent orchestration',
    ],

    # =========================================================================
    # WEB FRAMEWORKS - FRONTEND
    # =========================================================================
    'nextjs': [
        'next.js', 'nextjs', 'next/app', 'next/pages', 'next.config',
        'getserversideprops', 'getstaticprops', 'app router', 'pages router',
        'use client', 'use server', '@next/', 'next/image', 'next/link',
    ],
    'react': [
        'react', 'usestate', 'useeffect', 'jsx', 'tsx', 'react-dom',
        'createroot', 'usecontext', 'usereducer', 'react hook',
        'usememo', 'usecallback', 'useref', 'from react',
    ],
    'vue': [
        'vue.js', 'vuejs', 'vue 3', 'nuxt', 'composition api', 'pinia',
        'vuex', '.vue', 'definecomponent', 'ref(', 'reactive(',
    ],
    'svelte': [
        'svelte', 'sveltekit', 'svelte.config', '.svelte',
        'svelte/store', 'svelte/motion',
    ],
    'angular': [
        'angular', '@angular/', 'ng ', 'angular.json',
        '@component', '@injectable', 'ngmodule',
    ],
    'solid': [
        'solidjs', 'solid-js', 'from solid-js', 'createSignal',
        'solid.config',
    ],
    'qwik': [
        'qwik', '@builder.io/qwik', 'qwik-city',
    ],
    'astro': [
        'astro', 'astro.config', '.astro', 'astro:content',
    ],
    'remix': [
        'remix', '@remix-run', 'remix.config', 'loader function',
        'action function',
    ],
    'htmx': [
        'htmx', 'hx-get', 'hx-post', 'hx-trigger', 'hx-swap',
    ],

    # =========================================================================
    # WEB FRAMEWORKS - BACKEND
    # =========================================================================
    'fastapi': [
        'fastapi', 'from fastapi', '@app.get', '@app.post', 'uvicorn',
        'pydantic', 'fastapi.routing',
    ],
    'express': [
        'express.js', 'expressjs', 'app.get(', 'app.post(', 'express()',
        'express.router', 'app.use(', 'require("express")',
    ],
    'flask': [
        'from flask', 'flask app', '@app.route', 'flask_',
        'flask.blueprint',
    ],
    'django': [
        'django', 'from django', 'django.db', 'django rest', 'drf',
        'django.contrib', 'manage.py', 'settings.py',
    ],
    'hono': [
        'hono', 'from hono', 'hono/cloudflare', 'hono.js',
        'hono/zod-validator',
    ],
    'fastify': [
        'fastify', '@fastify/', 'fastify.register',
    ],
    'nest': [
        'nestjs', '@nestjs/', 'nest.js', '@controller', '@module',
        '@injectable',
    ],
    'rails': [
        'ruby on rails', 'rails', 'activerecord', 'actioncontroller',
        'gemfile', 'rake',
    ],
    'laravel': [
        'laravel', 'artisan', 'eloquent', 'blade', 'composer.json',
    ],
    'gin': [
        'gin-gonic', 'gin.', 'gin.context', 'gin.engine',
    ],
    'fiber': [
        'gofiber', 'fiber.', 'fiber.ctx', 'fiber.app',
    ],
    'axum': [
        'axum', 'tokio', 'axum::extract', 'axum::routing',
    ],
    'actix': [
        'actix', 'actix-web', 'actix_web', 'httpserver',
    ],

    # =========================================================================
    # CLOUD PROVIDERS & INFRASTRUCTURE - Tier 1 (Major Hyperscalers)
    # Based on 2025 market share: AWS 29%, Azure 22%, GCP 12%
    # =========================================================================
    'aws': [
        # Code-specific patterns (imports, SDK usage)
        'boto3', 'aws-sdk', '@aws-sdk/', 'import boto3', 'from boto3',
        'aws_access_key', 'aws_secret_key', 'aws.config', 'aws.s3',
        'new s3client', 'new dynamodbclient', 's3.putobject', 's3.getobject',
        'lambda.invoke', 'dynamodb.put', 'dynamodb.get', 'dynamodb.query',
        # Infrastructure as Code
        'cloudformation', 'aws cdk', 'from aws_cdk', '@aws-cdk/',
        'serverless.yml', 'sam template', 'aws::',
        # Specific service usage patterns
        'sagemaker', 'aws bedrock', 'bedrock-runtime', 'bedrockruntime',
    ],
    'azure': [
        'azure', 'microsoft azure', 'azure functions', 'azure blob',
        'cosmos db', 'azure ai', 'azure openai', 'azure devops',
        'azure cognitive', 'azure ml', 'azure arc', 'azure stack',
        'azure synapse', 'azure data factory', 'azure service bus',
        'azure event hubs', 'aks', 'azure container', 'azure app service',
        'azure key vault', 'azure ad', 'entra', 'power platform',
    ],
    'gcp': [
        'google cloud', 'gcp', 'cloud run', 'cloud functions',
        'firestore', 'gcloud', 'vertex ai', 'cloud storage', 'pubsub',
        'cloud sql', 'app engine', 'dataflow', 'dataproc', 'gke',
        'cloud spanner', 'cloud composer', 'cloud scheduler', 'cloud tasks',
        'cloud build', 'artifact registry', 'secret manager', 'cloud armor',
        'cloud cdn', 'anthos', 'dialogflow', 'document ai',
    ],
    'bigquery': [
        'bigquery', 'big query', 'bq ', 'google-cloud-bigquery',
        'from google.cloud import bigquery', 'bigquery.client', 'bq query',
        'bigquery ml', 'bigquery omni',
    ],

    # =========================================================================
    # CLOUD PROVIDERS - Tier 2 (Major Enterprise & Regional)
    # =========================================================================
    'oracle-cloud': [
        'oracle cloud', 'oci', 'oracle cloud infrastructure',
        'autonomous database', 'cloud@customer', 'oracle apex',
        'oracle functions', 'oracle kubernetes', 'oke',
    ],
    'ibm-cloud': [
        'ibm cloud', 'ibm watson', 'ibm quantum', 'red hat openshift',
        'ibm cloud functions', 'ibm cloudant', 'ibm cos',
        'ibm code engine', 'ibm db2',
    ],
    'alibaba-cloud': [
        'alibaba cloud', 'aliyun', 'alicloud', 'alibaba ecs',
        'maxcompute', 'alibaba oss', 'function compute',
        'alibaba rds', 'polardb', 'analyticdb',
    ],
    'tencent-cloud': [
        'tencent cloud', 'tencent', 'qcloud', 'tencent cos',
        'tencent cvm', 'tencent cdn', 'tencent scf',
    ],
    'huawei-cloud': [
        'huawei cloud', 'hwcloud', 'huawei obs', 'huawei ecs',
    ],

    # =========================================================================
    # CLOUD PROVIDERS - Tier 3 (Developer-Focused & SMB)
    # =========================================================================
    'cloudflare': [
        'cloudflare', 'workers', 'wrangler', 'cf-', 'd1 database',
        'cloudflare pages', 'workers ai', 'r2', 'kv namespace',
        'durable objects', 'cloudflare tunnel', 'cloudflare images',
        'cloudflare stream', 'hyperdrive', 'vectorize',
    ],
    'vercel': [
        'vercel', 'vercel.json', 'vercel deploy', 'vercel cli',
        '@vercel/', 'vercel/og', 'edge runtime', 'vercel kv',
        'vercel postgres', 'vercel blob', 'vercel ai',
    ],
    'netlify': [
        'netlify', 'netlify.toml', 'netlify functions', 'netlify edge',
        'netlify identity', 'netlify cms', 'netlify graph',
    ],
    'railway': [
        'railway', 'railway.app', 'railway.toml', 'railway deploy',
        'railway cli',
    ],
    'fly-io': [
        'fly.io', 'flyctl', 'fly.toml', 'fly deploy', 'fly machine',
        'fly postgres', 'fly proxy',
    ],
    'render': [
        'render.com', 'render.yaml', 'render deploy', 'render service',
    ],
    'digital-ocean': [
        'digitalocean', 'digital ocean', 'do spaces', 'droplet',
        'doctl', 'app platform', 'do kubernetes', 'doks',
    ],
    'linode': [
        'linode', 'akamai cloud', 'akamai connected cloud',
        'linode kubernetes', 'lke', 'linode object storage',
    ],
    'vultr': [
        'vultr', 'vultr cloud', 'vultr gpu', 'vultr kubernetes',
    ],
    'hetzner': [
        'hetzner', 'hetzner cloud', 'hcloud',
    ],
    'ovh': [
        'ovh', 'ovhcloud', 'ovh cloud',
    ],

    # =========================================================================
    # MANAGED DATA PLATFORMS & SAAS
    # =========================================================================
    'snowflake': [
        'snowflake', 'snowflake cloud', 'snowflake db', 'snowpark',
        'snowflake warehouse', 'snowflake connector', 'snowflake cortex',
        'snowflake native app',
    ],
    'databricks': [
        'databricks', 'databricks unity', 'unity catalog', 'delta lake',
        'databricks sql', 'mlflow', 'databricks workspace',
        'lakehouse', 'databricks notebook',
    ],
    'confluent': [
        'confluent', 'confluent cloud', 'confluent kafka', 'ksqldb',
        'schema registry', 'confluent connector', 'tableflow',
        'confluent platform',
    ],
    'mongodb-atlas': [
        'mongodb atlas', 'atlas', 'mongo atlas', 'atlas search',
        'atlas data lake', 'realm', 'atlas triggers',
    ],
    'elastic-cloud': [
        'elastic cloud', 'elasticsearch cloud', 'elastic.co',
    ],

    # =========================================================================
    # ENTERPRISE SAAS PLATFORMS
    # =========================================================================
    'salesforce': [
        'salesforce', 'salesforce cloud', 'salesforce crm', 'heroku',
        'salesforce api', 'apex', 'visualforce', 'lightning',
        'salesforce commerce', 'mulesoft',
    ],
    'sap': [
        'sap', 'sap cloud', 'sap hana', 's/4hana', 'sap btp',
        'sap integration', 'sap erp', 'sap analytics',
    ],
    'servicenow': [
        'servicenow', 'service now', 'now platform',
    ],
    'workday': [
        'workday', 'workday api',
    ],

    # =========================================================================
    # CONTAINER & ORCHESTRATION
    # =========================================================================
    'docker': [
        'docker', 'dockerfile', 'docker-compose', 'container',
        'docker build', 'docker run', 'docker hub', 'docker swarm',
    ],
    'kubernetes': [
        'kubernetes', 'k8s', 'kubectl', 'helm', 'deployment.yaml',
        'pod', 'service.yaml', 'ingress', 'configmap', 'kustomize',
        'argocd', 'flux', 'istio', 'linkerd',
    ],
    'terraform': [
        'terraform', 'tf.', '.tf', 'terraform plan', 'terraform apply',
        'terraform.tfstate', 'hcl', 'terragrunt', 'terraform cloud',
    ],
    'pulumi': [
        'pulumi', 'pulumi up', 'pulumi.config', 'pulumi cloud',
    ],
    'ansible': [
        'ansible', 'ansible-playbook', 'ansible.cfg', 'playbook.yml',
    ],

    # =========================================================================
    # DATABASES - RELATIONAL
    # =========================================================================
    'postgresql': [
        'postgres', 'postgresql', 'psql', 'pg_', 'pgvector',
    ],
    'mysql': [
        'mysql', 'mariadb', 'mysqld',
    ],
    'sqlite': [
        'sqlite', 'sqlite3', 'better-sqlite3', 'sql.js',
    ],
    'supabase': [
        'supabase', 'supabase-js', '@supabase/supabase-js',
        'supabase.co', 'supabase client',
    ],
    'neon': [
        'neon', 'neon.tech', '@neondatabase', 'neon serverless',
    ],
    'planetscale': [
        'planetscale', 'pscale', '@planetscale',
    ],
    'turso': [
        'turso', 'turso.io', '@libsql',
    ],

    # =========================================================================
    # DATABASES - NOSQL
    # =========================================================================
    'mongodb': [
        'mongodb', 'mongoose', 'mongo', 'pymongo',
        'mongoclient', 'mongodb atlas',
    ],
    'redis': [
        'redis', 'ioredis', 'redis-cli', 'upstash',
        'redisclient', 'redis cloud',
    ],
    'dynamodb': [
        'dynamodb', 'dynamo', 'aws dynamodb', 'dynamodb-local',
    ],
    'firebase': [
        'firebase', 'firestore', 'realtime database', '@firebase/',
        'firebase auth', 'firebase functions',
    ],
    'cassandra': [
        'cassandra', 'datastax', 'cql', 'scylla',
    ],

    # =========================================================================
    # DATABASES - VECTOR
    # =========================================================================
    'pinecone': [
        'pinecone', 'pinecone-client', 'pinecone.init',
        'pinecone index', 'pinecone.from_documents',
    ],
    'weaviate': [
        'weaviate', 'weaviate-client', 'weaviate.io',
        'weaviate_client',
    ],
    'qdrant': [
        'qdrant', 'qdrant-client', 'qdrant_client',
        'qdrantclient',
    ],
    'chromadb': [
        'chromadb', 'chroma', 'chromadb.client',
        'chroma_client', 'chromadb.persistentclient',
    ],
    'milvus': [
        'milvus', 'pymilvus', 'milvus.client',
        'zilliz',
    ],
    'pgvector': [
        'pgvector', 'pg_vector', 'vector extension',
    ],
    'faiss': [
        'faiss', 'faiss-cpu', 'faiss-gpu', 'faiss.indexflat',
    ],

    # =========================================================================
    # DATABASES - GRAPH
    # =========================================================================
    'neo4j': [
        'neo4j', 'cypher', 'neo4j-driver', 'py2neo',
        'neo4j graph', 'graphdatabase',
    ],
    'dgraph': [
        'dgraph', 'dgraph.io', 'pydgraph',
    ],
    'arangodb': [
        'arangodb', 'arango', 'aql',
    ],
    'tigergraph': [
        'tigergraph', 'gsql',
    ],
    'falkordb': [
        'falkordb', 'falkor', 'graphrag', 'falkordb-py',
        'from falkordb', 'falkor graph',
    ],
    'kuzu': [
        'kuzu', 'kuzudb', 'kuzu graph', 'from kuzu',
    ],
    'terminusdb': [
        'terminusdb', 'terminus', 'terminusdb-client',
    ],

    # =========================================================================
    # DATABASES - MULTI-MODEL & AI-NATIVE
    # =========================================================================
    'surrealdb': [
        'surrealdb', 'surreal', 'surrealql', 'surreal.new',
        'from surrealdb', 'surreal db',
    ],
    'duckdb': [
        'duckdb', 'duck db', 'duckdb-wasm', 'from duckdb',
        'duckdb.connect', 'motherduck',
    ],
    'lancedb': [
        'lancedb', 'lance db', 'lance format', 'from lancedb',
        'lancedb.connect', 'lance columnar',
    ],
    'edgedb': [
        'edgedb', 'edge db', 'edgeql', 'from edgedb',
    ],
    'tidb': [
        'tidb', 'ti db', 'pingcap', 'tidb cloud',
        'tidb serverless',
    ],
    'cockroachdb': [
        'cockroachdb', 'cockroach', 'crdb',
    ],
    'cozodb': [
        'cozodb', 'cozo', 'datalog',
    ],

    # =========================================================================
    # AI MEMORY & KNOWLEDGE GRAPHS
    # =========================================================================
    'graphiti': [
        'graphiti', 'graphiti-core', 'from graphiti', 'zep graphiti',
        'temporal knowledge graph',
    ],
    'mem0': [
        'mem0', 'mem0ai', 'from mem0',
    ],
    'zep': [
        'zep', 'zep-python', 'from zep_python', 'zep memory',
    ],
    'memgpt': [
        'memgpt', 'letta', 'from memgpt', 'from letta',
    ],

    # =========================================================================
    # ORMS & DATABASE TOOLS
    # =========================================================================
    'prisma': [
        'prisma', 'prisma.schema', 'prismaclient', '@prisma/client',
        'prisma migrate', 'prisma studio',
    ],
    'drizzle': [
        'drizzle', 'drizzle-orm', 'drizzle-kit',
    ],
    'sqlalchemy': [
        'sqlalchemy', 'from sqlalchemy', 'session.query',
    ],
    'typeorm': [
        'typeorm', '@entity', 'createconnection',
    ],
    'sequelize': [
        'sequelize', 'sequelize.define',
    ],
    'knex': [
        'knex', 'knex.js', 'knex(',
    ],
    'kysely': [
        'kysely', 'from kysely',
    ],

    # =========================================================================
    # SEARCH & ANALYTICS
    # =========================================================================
    'elasticsearch': [
        'elasticsearch', 'elastic', 'kibana', 'opensearch',
        'elasticsearch-py', '@elastic/elasticsearch',
    ],
    'algolia': [
        'algolia', 'algoliasearch', '@algolia/',
    ],
    'meilisearch': [
        'meilisearch', 'meili',
    ],
    'typesense': [
        'typesense',
    ],

    # =========================================================================
    # EXTERNAL DATA SOURCES & APIS
    # =========================================================================
    'pubmed': [
        'pubmed', 'ncbi', 'entrez', 'biopython', 'pubmed api',
        'medline', 'pubmed central', 'pmid', 'pmcid',
    ],

    # -------------------------------------------------------------------------
    # PREPRINT SERVERS / XIVs - Comprehensive list of academic preprint archives
    # -------------------------------------------------------------------------
    # Major General-Purpose
    'arxiv': [
        'arxiv', 'arxiv api', 'arxiv.org', 'arxiv.abs', 'arxiv id',
    ],
    'osf-preprints': [
        'osf preprints', 'osf.io/preprints', 'open science framework',
    ],
    'preprints-org': [
        'preprints.org', 'mdpi preprints',
    ],
    'zenodo': [
        'zenodo', 'zenodo.org', 'zenodo api',
    ],
    'figshare': [
        'figshare', 'figshare.com',
    ],
    'ssrn': [
        'ssrn', 'social science research network', 'ssrn.com',
    ],
    'research-square': [
        'research square', 'researchsquare.com',
    ],

    # Life Sciences / Biology / Medicine
    'biorxiv': [
        'biorxiv', 'bioRxiv', 'biorxiv.org', 'bio-rxiv', 'bio rxiv',
    ],
    'medrxiv': [
        'medrxiv', 'medRxiv', 'medrxiv.org', 'med-rxiv', 'med rxiv',
    ],
    'chemrxiv': [
        'chemrxiv', 'chemRxiv', 'chemrxiv.org', 'chem-rxiv', 'chem rxiv',
    ],
    'agrirxiv': [
        'agrirxiv', 'agriRxiv', 'agrirxiv.org', 'agri-rxiv', 'agrixiv',
    ],
    'nutrixiv': [
        'nutrixiv', 'nutriXiv', 'nutri-rxiv',
    ],
    'paleorxiv': [
        'paleorxiv', 'paleorXiv', 'paleorxiv.org', 'paleo-rxiv',
    ],
    'ecoevorxiv': [
        'ecoevorxiv', 'ecoEvoRxiv', 'ecology evolution rxiv',
    ],
    'biohackrxiv': [
        'biohackrxiv', 'bioHackrXiv', 'biohackathon',
    ],
    'mitofitpreprints': [
        'mitofit', 'mitofit preprints',
    ],

    # Earth & Environmental Sciences
    'eartharxiv': [
        'eartharxiv', 'EarthArXiv', 'eartharxiv.org', 'earth-arxiv',
    ],
    'essoar': [
        'essoar', 'ESSOAr', 'earth space science open archive',
    ],
    'marxiv': [
        'marxiv', 'MarXiv', 'marine arxiv', 'ocean science preprint',
    ],

    # Physics / Math / Computer Science (covered by arxiv above)
    'vixra': [
        'vixra', 'viXra', 'vixra.org',
    ],

    # Engineering & Technology
    'techrxiv': [
        'techrxiv', 'TechRxiv', 'techrxiv.org', 'tech-rxiv', 'ieee preprint',
    ],
    'engrxiv': [
        'engrxiv', 'engrXiv', 'engrxiv.org', 'engr-xiv', 'engineering arxiv',
    ],
    'ecsarxiv': [
        'ecsarxiv', 'ECSarXiv', 'electrochemistry preprint',
    ],

    # Social Sciences & Humanities
    'socarxiv': [
        'socarxiv', 'SocArXiv', 'socarxiv.org', 'soc-arxiv', 'social science arxiv',
    ],
    'psyarxiv': [
        'psyarxiv', 'PsyArXiv', 'psyarxiv.org', 'psy-arxiv', 'psychology arxiv',
    ],
    'edarxiv': [
        'edarxiv', 'EdArXiv', 'edarxiv.org', 'ed-arxiv', 'education arxiv',
    ],
    'lawarxiv': [
        'lawarxiv', 'LawArXiv', 'lawarxiv.org', 'law-arxiv', 'legal preprint',
    ],
    'metaarxiv': [
        'metaarxiv', 'MetaArXiv', 'metaarxiv.org', 'meta-arxiv', 'meta research',
    ],
    'mindrxiv': [
        'mindrxiv', 'MindRxiv', 'mind-rxiv', 'contemplative science',
    ],
    'mediarxiv': [
        'mediarxiv', 'MediArXiv', 'media studies preprint', 'film studies preprint',
    ],
    'sportrxiv': [
        'sportrxiv', 'SportRxiv', 'sportrχiv', 'sport-rxiv', 'sports science preprint',
    ],
    'philarchive': [
        'philarchive', 'PhilArchive', 'philosophy archive',
    ],
    'philsci-archive': [
        'philsci archive', 'philsci-archive', 'philosophy of science archive',
    ],
    'apsa-preprints': [
        'apsa preprints', 'political science preprint',
    ],
    'bodoarxiv': [
        'bodoarxiv', 'BodoArXiv', 'medieval studies preprint',
    ],
    'lissa': [
        'lissa', 'lis scholarship archive', 'library science preprint',
    ],

    # Regional / Language-Specific
    'africarxiv': [
        'africarxiv', 'AfricArXiv', 'africarxiv.org', 'africa-rxiv', 'african research',
    ],
    'indiarxiv': [
        'indiarxiv', 'IndiaRxiv', 'indiarxiv.org', 'india-rxiv', 'indian research',
    ],
    'arabixiv': [
        'arabixiv', 'Arabixiv', 'arabixiv.org', 'arabic preprint',
    ],
    'frenxiv': [
        'frenxiv', 'Frenxiv', 'french preprint',
    ],
    'inarxiv': [
        'inarxiv', 'INA-Rxiv', 'indonesia preprint', 'indonesian research',
    ],
    'jxiv': [
        'jxiv', 'Jxiv', 'japanese preprint',
    ],
    'scielo-preprints': [
        'scielo preprints', 'scielo', 'latin america preprint',
    ],
    'preprints-ru': [
        'preprints.ru', 'russian preprint',
    ],

    # Multidisciplinary Platforms
    'f1000research': [
        'f1000research', 'f1000 research', 'faculty opinions',
    ],
    'wellcome-open': [
        'wellcome open research', 'wellcome open',
    ],
    'gates-open': [
        'gates open research', 'gates foundation',
    ],
    'authorea': [
        'authorea', 'authorea.com',
    ],
    'peerj-preprints': [
        'peerj preprints', 'peerj.com/preprints',
    ],
    'researchgate': [
        'researchgate', 'researchgate.net',
    ],
    'academia-edu': [
        'academia.edu', 'academia preprint',
    ],

    # Specialized Archives
    'cryptology-eprint': [
        'cryptology eprint', 'iacr eprint', 'eprint.iacr.org', 'crypto preprint',
    ],
    'repec': [
        'repec', 'research papers in economics', 'ideas.repec.org',
    ],
    'econstor': [
        'econstor', 'zbw', 'economics preprint',
    ],
    'thesis-commons': [
        'thesis commons', 'thesiscommons',
    ],
    'focus-archive': [
        'focus archive', 'focusarchive',
    ],
    'alphaxiv': [
        'alphaxiv', 'alphaXiv', 'alphaxiv.org',
    ],

    # Publisher Preprint Platforms
    'lancet-preprints': [
        'preprints with the lancet', 'lancet preprint', 'ssrn lancet',
    ],
    'cambridge-engage': [
        'cambridge open engage', 'cambridge engage',
    ],
    'sage-advance': [
        'sage advance', 'advance sage preprints',
    ],
    'jmir-preprints': [
        'jmir preprints', 'jmir.org/preprints',
    ],
    'beilstein-archives': [
        'beilstein archives', 'beilstein preprint',
    ],
    'arpha-preprints': [
        'arpha preprints', 'pensoft preprint',
    ],

    'semantic-scholar': [
        'semantic scholar', 'semanticscholar', 's2_', 'paper api',
    ],
    'openalex': [
        'openalex', 'open alex',
    ],
    'crossref': [
        'crossref', 'doi.org',
    ],
    'wikipedia': [
        'wikipedia', 'wikimedia', 'wikidata', 'mediawiki',
    ],
    'twitter-api': [
        'twitter api', 'tweepy', 'twitter-api-v2', 'x api',
    ],
    'github-api': [
        'github api', 'octokit', 'pygithub', 'gh api',
    ],
    'notion-api': [
        'notion api', '@notionhq', 'notion-client', 'notion.so',
    ],
    'slack-api': [
        'slack api', 'slack-bolt', '@slack/bolt', 'slack webhook',
    ],
    'discord-api': [
        'discord.py', 'discord.js', 'discord api', 'discord bot',
    ],
    'stripe': [
        'stripe', 'stripe.com', 'stripe api', 'payment_intent',
        '@stripe/', 'stripe-js',
    ],
    'twilio': [
        'twilio', 'twilio api', 'twilio sms',
    ],
    'sendgrid': [
        'sendgrid', '@sendgrid/',
    ],
    'resend': [
        'resend', 'resend.com', '@resend/',
    ],

    # =========================================================================
    # AI/ML PROVIDERS
    # =========================================================================
    'anthropic': [
        'anthropic', 'claude api', 'claude-3', 'from anthropic',
        '@anthropic-ai/sdk', 'anthropic.messages', 'claude-opus',
        'claude-sonnet', 'claude-haiku',
    ],
    'openai': [
        'openai', 'gpt-4', 'gpt-3', 'chatgpt', 'from openai',
        'openai.chat', 'openai api', 'gpt-4o', 'o1',
    ],
    'google-ai': [
        'google ai', 'gemini', 'palm', 'google.generativeai',
        'gemini-pro', 'gemini-ultra',
    ],
    'mistral': [
        'mistral', 'mistral ai', 'mistral-large', 'mixtral',
    ],
    'cohere': [
        'cohere', 'cohere.ai', 'cohere api',
    ],
    'replicate': [
        'replicate', 'replicate.run', 'replicate.com',
    ],
    'huggingface': [
        'huggingface', 'transformers', 'from transformers', 'hf_',
        'hugging face', 'datasets', '@huggingface/',
    ],
    'groq': [
        'groq', 'groq cloud', 'groq api',
    ],
    'together-ai': [
        'together ai', 'together.ai', 'togetherai',
    ],
    'fireworks-ai': [
        'fireworks ai', 'fireworks.ai',
    ],

    # =========================================================================
    # AI/ML LIBRARIES
    # =========================================================================
    'pytorch': [
        'pytorch', 'torch', 'import torch', 'nn.module',
        'torch.nn', 'torch.optim',
    ],
    'tensorflow': [
        'tensorflow', 'import tensorflow', 'tf.keras', 'keras',
    ],
    'jax': [
        'jax', 'import jax', 'jax.numpy', 'flax',
    ],
    'sklearn': [
        'sklearn', 'scikit-learn', 'from sklearn',
    ],
    'pandas': [
        'pandas', 'import pandas', 'pd.dataframe',
    ],
    'numpy': [
        'numpy', 'import numpy', 'np.array',
    ],
    'scipy': [
        'scipy', 'from scipy',
    ],
    'matplotlib': [
        'matplotlib', 'pyplot', 'plt.plot',
    ],
    'plotly': [
        'plotly', 'plotly.express', 'plotly.graph_objects',
    ],

    # =========================================================================
    # TESTING & QUALITY
    # =========================================================================
    'jest': [
        'jest', 'describe(', 'it(', 'expect(', 'jest.config',
        'jest.mock', '@jest/',
    ],
    'vitest': [
        'vitest', 'vitest.config', 'from vitest',
    ],
    'pytest': [
        'pytest', 'def test_', '@pytest', 'pytest.ini',
        'pytest.fixture',
    ],
    'playwright': [
        'playwright', '@playwright/test', 'page.goto',
        'page.click', 'page.fill',
    ],
    'cypress': [
        'cypress', 'cy.', 'cypress.config',
    ],
    'mocha': [
        'mocha', 'describe(', 'it(',
    ],
    'testing-library': [
        'testing-library', '@testing-library/', 'render(',
        'screen.', 'fireEvent',
    ],

    # =========================================================================
    # BUILD TOOLS & PACKAGE MANAGERS
    # =========================================================================
    'vite': [
        'vite', 'vite.config', 'vitejs',
    ],
    'webpack': [
        'webpack', 'webpack.config',
    ],
    'esbuild': [
        'esbuild', 'esbuild.build',
    ],
    'rollup': [
        'rollup', 'rollup.config',
    ],
    'parcel': [
        'parcel', 'parcel-bundler',
    ],
    'turborepo': [
        'turborepo', 'turbo.json', 'turbo run',
    ],
    'nx': [
        'nx workspace', 'nx.json', 'nx run',
    ],
    'lerna': [
        'lerna', 'lerna.json',
    ],
    'pnpm': [
        'pnpm', 'pnpm-workspace', 'pnpm install',
    ],
    'bun': [
        'bun', 'bunx', 'bun.lockb', 'bun run',
    ],
    'deno': [
        'deno', 'deno.json', 'deno run', 'deno deploy',
    ],

    # =========================================================================
    # MOBILE
    # =========================================================================
    'react-native': [
        'react native', 'react-native', 'eas build',
        'metro.config', 'expo-router', 'expo-cli', 'expo start',
        'react-native-', 'expo install', 'expo sdk', 'expo.dev',
        'from react-native', '@react-native', 'npx expo',
    ],
    'flutter': [
        'flutter', 'dart', 'pubspec.yaml', 'widget',
    ],
    'swift': [
        'swift', 'swiftui', 'uikit', 'xcodeproj',
    ],
    'kotlin': [
        'kotlin', 'jetpack compose', 'android studio',
    ],
    'capacitor': [
        'capacitor', '@capacitor/', 'capacitor.config',
    ],
    'tauri': [
        'tauri', 'tauri.conf', '@tauri-apps/',
    ],
    'electron': [
        'electron', 'electronjs', 'electron-builder',
    ],

    # =========================================================================
    # STYLING & UI
    # =========================================================================
    'tailwindcss': [
        'tailwind', 'tailwindcss', 'tailwind.config', '@apply',
    ],
    'shadcn': [
        'shadcn', 'shadcn/ui', '@/components/ui',
    ],
    'radix': [
        'radix', '@radix-ui/', 'radix-ui',
    ],
    'chakra': [
        'chakra', '@chakra-ui/', 'chakra-ui',
    ],
    'material-ui': [
        'material-ui', '@mui/', 'material ui',
    ],
    'ant-design': [
        'antd', 'ant design', 'ant-design',
    ],
    'styled-components': [
        'styled-components', 'styled.', 'createGlobalStyle',
    ],
    'emotion': [
        '@emotion/', 'emotion/styled', 'emotion css',
    ],

    # =========================================================================
    # API & DATA TRANSFER
    # =========================================================================
    'graphql': [
        'graphql', 'gql`', 'apollo', 'urql', 'type query',
        '@apollo/', 'graphql-yoga',
    ],
    'trpc': [
        'trpc', '@trpc', 'trpc.', 'createtrpcrouter',
    ],
    'grpc': [
        'grpc', 'protobuf', '.proto',
    ],
    'websocket': [
        'websocket', 'socket.io', 'ws://', 'wss://', 'socket.on',
    ],
    'rest': [
        'rest api', 'restful', 'openapi', 'swagger',
    ],

    # =========================================================================
    # AUTHENTICATION
    # =========================================================================
    'auth0': [
        'auth0', '@auth0',
    ],
    'clerk': [
        'clerk', '@clerk', 'clerkprovider',
    ],
    'nextauth': [
        'nextauth', 'next-auth', '@auth/',
    ],
    'lucia': [
        'lucia', 'lucia-auth',
    ],
    'passport': [
        'passport', 'passport.js', 'passport-local',
    ],
    'supabase-auth': [
        'supabase auth', 'supabase.auth',
    ],
    'firebase-auth': [
        'firebase auth', 'firebase.auth',
    ],

    # =========================================================================
    # VALIDATION & SCHEMAS
    # =========================================================================
    'zod': [
        'zod', 'z.object', 'z.string', 'zodschema',
    ],
    'yup': [
        'yup', 'yup.object', 'yup.string',
    ],
    'joi': [
        'joi', 'joi.object',
    ],
    'valibot': [
        'valibot', 'from valibot',
    ],
    'arktype': [
        'arktype', 'from arktype',
    ],

    # =========================================================================
    # OBSERVABILITY & MONITORING
    # =========================================================================
    'sentry': [
        'sentry', '@sentry/', 'sentry.io',
    ],
    'datadog': [
        'datadog', 'dd-trace',
    ],
    'newrelic': [
        'newrelic', 'new relic',
    ],
    'grafana': [
        'grafana', 'prometheus', 'loki',
    ],
    'posthog': [
        'posthog', 'posthog-js',
    ],
    'mixpanel': [
        'mixpanel',
    ],
    'amplitude': [
        'amplitude',
    ],
    'langfuse': [
        'langfuse', 'langfuse.com',
    ],
    'langsmith': [
        'langsmith', 'langsmith.com',
    ],

    # =========================================================================
    # STATE MANAGEMENT
    # =========================================================================
    'redux': [
        'redux', '@reduxjs/toolkit', 'createSlice',
    ],
    'zustand': [
        'zustand', 'create(', 'useStore',
    ],
    'jotai': [
        'jotai', 'atom(', 'useAtom',
    ],
    'recoil': [
        'recoil', 'RecoilRoot', 'atom(',
    ],
    'mobx': [
        'mobx', 'observable', 'makeAutoObservable',
    ],
    'tanstack-query': [
        'tanstack query', 'react-query', '@tanstack/react-query',
        'useQuery', 'useMutation',
    ],
    'swr': [
        'swr', 'useSWR',
    ],

    # =========================================================================
    # CMS & CONTENT
    # =========================================================================
    'contentful': [
        'contentful', '@contentful/',
    ],
    'sanity': [
        'sanity', 'sanity.io', '@sanity/',
    ],
    'strapi': [
        'strapi',
    ],
    'payload': [
        'payload cms', 'payloadcms',
    ],
    'directus': [
        'directus',
    ],
    'ghost': [
        'ghost cms', '@tryghost/',
    ],

    # =========================================================================
    # MESSAGE QUEUES & EVENTS
    # =========================================================================
    'kafka': [
        'kafka', 'kafkajs', 'confluent',
    ],
    'rabbitmq': [
        'rabbitmq', 'amqp', 'pika',
    ],
    'bullmq': [
        'bullmq', 'bull queue', 'new bull(', 'bull.process', 'bull.add',
        'from bull', 'require("bull")', "require('bull')",
    ],
    'celery': [
        'celery', 'from celery',
    ],
    'inngest': [
        'inngest', '@inngest/',
    ],
    'trigger-dev': [
        'trigger.dev', '@trigger.dev/',
    ],
}


# =============================================================================
# PROJECT COMPONENT TYPES
# =============================================================================
# Components that projects can have (browser extensions, APIs, etc.)

PROJECT_COMPONENTS = {
    # Browser Extensions
    'chrome-extension': [
        'manifest.json', 'manifest_version', 'chrome.runtime', 'chrome.tabs',
        'chrome.storage', 'content_script', 'background.js', 'popup.html',
        'browser extension', 'chrome extension', 'firefox extension',
    ],
    'vscode-extension': [
        'vscode extension', 'extension.ts', 'activate(context)', 'vscode.commands',
        'contributes', 'extensionKind',
    ],

    # Frontend Components
    'web-frontend': [
        'src/frontend', 'src/web', 'src/client', 'pages/', 'components/',
        'app.tsx', 'main.tsx', 'index.html', 'vite.config',
    ],
    'mobile-app': [
        'react native', 'react-native', 'ios/', 'android/',
        'metro.config', 'eas.json', 'capacitor', 'expo-router',
        'expo-cli', 'expo.dev', 'npx expo',
    ],
    'desktop-app': [
        'electron', 'tauri', 'main.electron', 'preload.js',
    ],

    # Backend Components
    'api-server': [
        'src/api', 'api/', 'endpoints', 'routes/', 'controllers/',
        'main.py', 'app.py', 'server.ts', 'fastapi', 'express',
    ],
    'graphql-api': [
        'graphql', 'schema.graphql', 'resolvers/', 'typedefs',
        'apollo server', 'type query', 'type mutation',
    ],
    'websocket-server': [
        'websocket', 'socket.io', 'ws server', 'realtime',
    ],

    # Data & AI Components
    'ml-pipeline': [
        'ml/', 'models/', 'training/', 'inference/', 'pipeline',
        'torch', 'tensorflow', 'sklearn', 'model.py',
    ],
    'data-ingestion': [
        'ingestion/', 'etl/', 'pipeline/', 'scrapers/', 'crawlers/',
        'data loader', 'batch process',
    ],
    'knowledge-graph': [
        'graph/', 'neo4j', 'graphrag', 'knowledge graph', 'ontology',
        'triple store', 'rdf', 'sparql',
    ],
    'rag-system': [
        'rag', 'retrieval', 'embeddings', 'vector store', 'semantic search',
    ],

    # Infrastructure Components
    'kubernetes': [
        'k8s/', 'kubernetes/', 'helm/', 'deployment.yaml',
        'service.yaml', 'configmap', 'kustomize',
    ],
    'docker-compose': [
        'docker-compose', 'compose.yml', 'compose.yaml',
        'services:', 'container',
    ],
    'ci-cd-pipeline': [
        '.github/workflows', 'gitlab-ci', 'jenkinsfile',
        'ci/', 'cd/', 'pipeline.yml',
    ],

    # Other Components
    'cli-tool': [
        'cli/', 'bin/', 'commander', 'yargs', 'argparse',
        'command line', 'terminal',
    ],
    'sdk-library': [
        'sdk/', 'lib/', 'packages/', 'npm publish', 'pypi',
        'library', 'package',
    ],
    'mcp-server': [
        'mcp server', 'mcp.json', 'model context protocol',
        'mcp-server', 'mcpServers',
    ],
    'agent-system': [
        'agents/', '.agents/', 'agent orchestration', 'multi-agent',
        'swarm', 'crew', 'hive',
    ],
}


# =============================================================================
# CODING CONCEPTS & PATTERNS
# =============================================================================

CODING_CONCEPTS = {
    # Architecture Patterns
    'microservices': ['microservice', 'service mesh', 'api gateway', 'service discovery'],
    'monorepo': ['monorepo', 'turborepo', 'nx workspace', 'lerna', 'pnpm workspace'],
    'serverless': ['serverless', 'lambda', 'cloud functions', 'edge functions'],
    'event-driven': ['event driven', 'event sourcing', 'cqrs', 'message queue', 'pub/sub'],
    'clean-architecture': ['clean architecture', 'hexagonal', 'domain driven', 'ddd'],

    # Code Quality
    'testing': ['unit test', 'integration test', 'e2e test', 'test coverage', 'tdd', 'bdd'],
    'linting': ['eslint', 'prettier', 'biome', 'ruff', 'black', 'flake8'],
    'typescript-strict': ['strict mode', 'strictnullchecks', 'noimplicitany', 'type safety'],
    'ci-cd': ['github actions', 'ci/cd', 'gitlab ci', 'jenkins', 'circleci', 'continuous integration'],
    'documentation': ['jsdoc', 'typedoc', 'swagger', 'openapi', 'readme', 'docstring'],

    # Design Patterns
    'dependency-injection': ['dependency injection', 'ioc', 'inversion of control', 'di container'],
    'factory-pattern': ['factory pattern', 'abstract factory', 'createinstance'],
    'singleton': ['singleton', 'getinstance'],
    'observer': ['observer pattern', 'subscribe', 'publish', 'event emitter'],
    'repository-pattern': ['repository pattern', 'data access layer', 'dal'],

    # Modern Practices
    'api-first': ['api first', 'openapi', 'swagger', 'api design'],
    'type-safety': ['type safe', 'strongly typed', 'typescript', 'type inference'],
    'immutability': ['immutable', 'readonly', 'const', 'freeze'],
    'functional': ['functional programming', 'pure function', 'higher order', 'map reduce'],
    'reactive': ['reactive', 'rxjs', 'observable', 'signal', 'effect'],

    # Security
    'authentication': ['oauth', 'jwt', 'auth', 'login', 'session', 'token'],
    'authorization': ['rbac', 'acl', 'permission', 'role based'],
    'encryption': ['encrypt', 'hash', 'bcrypt', 'crypto', 'ssl', 'tls'],
    'input-validation': ['validate', 'sanitize', 'escape', 'xss', 'injection'],

    # Performance
    'caching': ['cache', 'redis', 'memcached', 'cdn', 'memoize'],
    'optimization': ['optimize', 'performance', 'lazy load', 'code split', 'tree shake'],
    'async-patterns': ['async await', 'promise', 'concurrent', 'parallel', 'worker'],
    'streaming': ['stream', 'chunk', 'buffer', 'pipe'],

    # Agentic Orchestration Patterns
    'graph-orchestration': [
        'graph orchestration', 'langgraph', 'dag', 'directed acyclic',
        'node graph', 'workflow graph', 'state graph', 'graph-based',
        'graph execution', 'dependency graph',
    ],
    'hierarchical-orchestration': [
        'hierarchical', 'tree structure', 'parent agent', 'child agent',
        'supervisor', 'manager agent', 'worker agent', 'delegation',
        'top-down', 'chain of command', 'crew', 'crewai',
    ],
    'swarm-orchestration': [
        'swarm', 'swarm intelligence', 'emergent', 'decentralized',
        'peer-to-peer', 'consensus', 'distributed agents', 'hive mind',
    ],
    'pipeline-orchestration': [
        'pipeline', 'sequential', 'chain', 'step-by-step',
        'workflow pipeline', 'stage', 'phase',
    ],
}


# =============================================================================
# TECHNOLOGY PATTERNS (for README analysis)
# =============================================================================

TECH_PATTERNS = {
    'python': [r'\.py\b', r'python', r'pip install', r'requirements\.txt', r'pyproject\.toml'],
    'typescript': [r'\.ts\b', r'typescript', r'\.tsx\b'],
    'javascript': [r'\.js\b', r'javascript', r'node', r'npm', r'yarn'],
    'react': [r'react', r'jsx', r'tsx', r'next\.js', r'nextjs'],
    'vue': [r'vue', r'\.vue\b', r'nuxt'],
    'rust': [r'\.rs\b', r'cargo', r'rust'],
    'go': [r'\.go\b', r'golang', r'go mod'],
    'java': [r'\.java\b', r'maven', r'gradle'],
    'kotlin': [r'\.kt\b', r'kotlin'],
    'swift': [r'\.swift\b', r'swiftui'],
    'csharp': [r'\.cs\b', r'dotnet', r'\.net'],
    'ruby': [r'\.rb\b', r'ruby', r'rails', r'gemfile'],
    'php': [r'\.php\b', r'laravel', r'composer'],
    'cloudflare': [r'cloudflare', r'workers', r'wrangler', r'cf-'],
    'docker': [r'docker', r'dockerfile', r'compose'],
    'kubernetes': [r'kubernetes', r'k8s', r'kubectl', r'helm'],
    'ai/ml': [r'anthropic', r'openai', r'llm', r'gpt', r'claude', r'transformer'],
    'database': [r'postgres', r'mysql', r'mongodb', r'redis', r'sqlite', r'supabase'],
}


# =============================================================================
# PROJECT CATEGORY PATTERNS
# =============================================================================

CATEGORY_PATTERNS = {
    'ai-agent': ['agent', 'agentic', 'autonomous', 'multi-agent', 'swarm', 'crew'],
    'scientific': ['coscientist', 'research', 'hypothesis', 'experiment', 'scientific', 'pubmed', 'arxiv'],
    'data-science': ['bigquery', 'analytics', 'data science', 'pandas', 'numpy', 'jupyter', 'datascience'],
    'web-app': ['frontend', 'backend', 'fullstack', 'web app', 'dashboard', 'saas'],
    'cli-tool': ['cli', 'command line', 'terminal'],
    'api': ['api', 'rest', 'graphql', 'endpoint', 'microservice'],
    'mobile': ['mobile', 'ios', 'android', 'react native', 'react-native', 'flutter', 'expo-router', 'metro.config'],
    'infrastructure': ['infra', 'devops', 'deploy', 'ci/cd', 'kubernetes', 'terraform'],
    'data': ['data', 'etl', 'pipeline', 'analytics', 'visualization', 'ingestion'],
    'ml': ['machine learning', 'ml', 'neural', 'training', 'inference', 'model'],
    'rag': ['rag', 'retrieval', 'vector', 'embeddings', 'semantic search'],
    'browser-extension': ['extension', 'chrome', 'firefox', 'browser'],
    'library': ['library', 'sdk', 'package', 'npm', 'pypi'],
}


# =============================================================================
# DISPLAY ICONS
# =============================================================================

FRAMEWORK_ICONS = {
    # AI/LLM Frameworks
    'claude-flow': '🌊', 'sparc': '⚡', 'agentic-engineering': '🤖',
    'coscientist': '🔬', 'mcp': '🔌', 'langchain': '🔗', 'langgraph': '📊',
    'crewai': '👥', 'autogen': '🤖', 'llamaindex': '🦙', 'openai-swarm': '🐝',
    'openai-agents-sdk': '🤖', 'dspy': '📐', 'semantic-kernel': '🧠',
    'haystack': '🔍',

    # Web Frameworks
    'nextjs': '▲', 'react': '⚛️', 'vue': '💚', 'svelte': '🔥',
    'angular': '🅰️', 'solid': '💎', 'qwik': '⚡', 'astro': '🚀',
    'remix': '💿', 'htmx': '📡',
    'fastapi': '⚡', 'express': '🚂', 'flask': '🧪', 'django': '🎸',
    'hono': '🔥', 'fastify': '⚡', 'nest': '🐱', 'rails': '💎',
    'laravel': '🐘', 'gin': '🍸', 'fiber': '⚡', 'axum': '🦀', 'actix': '🦀',

    # Cloud Providers - Tier 1
    'aws': '🟠', 'gcp': '🔵', 'azure': '🔷', 'bigquery': '📊',
    # Cloud Providers - Tier 2
    'oracle-cloud': '🔴', 'ibm-cloud': '🔵', 'alibaba-cloud': '🟠',
    'tencent-cloud': '🔵', 'huawei-cloud': '🔴',
    # Cloud Providers - Tier 3
    'cloudflare': '☁️', 'vercel': '▲', 'netlify': '🌐', 'railway': '🚂',
    'fly-io': '✈️', 'render': '🎨', 'digital-ocean': '🌊', 'linode': '🟢',
    'vultr': '🔷', 'hetzner': '🔴', 'ovh': '🔵',
    # Managed Data Platforms
    'snowflake': '❄️', 'databricks': '🧱', 'confluent': '🌀', 'mongodb-atlas': '🍃',
    'elastic-cloud': '🔍',
    # Enterprise SaaS
    'salesforce': '☁️', 'sap': '💎', 'servicenow': '🔧', 'workday': '📅',
    # Infrastructure
    'terraform': '🏗️', 'pulumi': '🔮', 'ansible': '🔧',
    'docker': '🐳', 'kubernetes': '☸️',

    # Databases
    'postgresql': '🐘', 'mysql': '🐬', 'sqlite': '📦',
    'supabase': '⚡', 'neon': '🌙', 'planetscale': '🪐', 'turso': '🔮',
    'mongodb': '🍃', 'redis': '🔴', 'dynamodb': '⚡', 'firebase': '🔥',
    'cassandra': '👁️',

    # Vector Databases
    'pinecone': '🌲', 'weaviate': '🕸️', 'qdrant': '📍', 'chromadb': '🎨',
    'milvus': '🔷', 'pgvector': '🐘', 'faiss': '📊',

    # Graph Databases
    'neo4j': '🔵', 'dgraph': '📊', 'arangodb': '🥑', 'tigergraph': '🐯',
    'falkordb': '🦅', 'kuzu': '🔷', 'terminusdb': '🔺',

    # Multi-Model & AI-Native Databases
    'surrealdb': '🌀', 'duckdb': '🦆', 'lancedb': '🗡️', 'edgedb': '⚡',
    'tidb': '📊', 'cockroachdb': '🪳', 'cozodb': '🧩',

    # AI Memory & Knowledge Graphs
    'graphiti': '🧠', 'mem0': '💭', 'zep': '⚡', 'memgpt': '🧠',

    # ORMs
    'prisma': '◭', 'drizzle': '💧', 'sqlalchemy': '🔮', 'typeorm': '📦',
    'sequelize': '📊', 'knex': '🔧', 'kysely': '🔮',

    # Search
    'elasticsearch': '🔍', 'algolia': '🔎', 'meilisearch': '🔍', 'typesense': '🔤',

    # External APIs & Data Sources
    'pubmed': '📚', 'semantic-scholar': '🎓',
    'openalex': '📖', 'crossref': '🔗', 'wikipedia': '📗',

    # Preprint Servers / XIVs
    # Major General-Purpose
    'arxiv': '📄', 'osf-preprints': '🔬', 'preprints-org': '📝',
    'zenodo': '🗃️', 'figshare': '📊', 'ssrn': '📑', 'research-square': '🔲',
    # Life Sciences / Biology / Medicine
    'biorxiv': '🧬', 'medrxiv': '🏥', 'chemrxiv': '⚗️', 'agrirxiv': '🌾',
    'nutrixiv': '🥗', 'paleorxiv': '🦴', 'ecoevorxiv': '🌿', 'biohackrxiv': '💻',
    'mitofitpreprints': '🔋',
    # Earth & Environmental Sciences
    'eartharxiv': '🌍', 'essoar': '🌌', 'marxiv': '🌊',
    # Physics / Alt
    'vixra': '📐',
    # Engineering & Technology
    'techrxiv': '⚙️', 'engrxiv': '🔧', 'ecsarxiv': '🔌',
    # Social Sciences & Humanities
    'socarxiv': '👥', 'psyarxiv': '🧠', 'edarxiv': '🎓', 'lawarxiv': '⚖️',
    'metaarxiv': '🔍', 'mindrxiv': '🧘', 'mediarxiv': '🎬', 'sportrxiv': '🏃',
    'philarchive': '📜', 'philsci-archive': '🔭', 'apsa-preprints': '🏛️',
    'bodoarxiv': '🏰', 'lissa': '📚',
    # Regional / Language-Specific
    'africarxiv': '🌍', 'indiarxiv': '🇮🇳', 'arabixiv': '🌙', 'frenxiv': '🇫🇷',
    'inarxiv': '🇮🇩', 'jxiv': '🇯🇵', 'scielo-preprints': '🌎', 'preprints-ru': '🇷🇺',
    # Multidisciplinary Platforms
    'f1000research': '🔬', 'wellcome-open': '💚', 'gates-open': '🌐',
    'authorea': '✍️', 'peerj-preprints': '👁️', 'researchgate': '🔗', 'academia-edu': '🎓',
    # Specialized Archives
    'cryptology-eprint': '🔐', 'repec': '💹', 'econstor': '📈',
    'thesis-commons': '📖', 'focus-archive': '🎯', 'alphaxiv': '🔤',
    # Publisher Preprint Platforms
    'lancet-preprints': '🩺', 'cambridge-engage': '📕', 'sage-advance': '📗',
    'jmir-preprints': '💻', 'beilstein-archives': '🧪', 'arpha-preprints': '🦎',
    'twitter-api': '🐦', 'github-api': '🐙', 'notion-api': '📝',
    'slack-api': '💬', 'discord-api': '🎮',
    'stripe': '💳', 'twilio': '📱', 'sendgrid': '📧', 'resend': '📤',

    # AI/ML Providers
    'anthropic': '🤖', 'openai': '🤖', 'google-ai': '🔮', 'mistral': '🌀',
    'cohere': '🔷', 'replicate': '🔁', 'huggingface': '🤗',
    'groq': '⚡', 'together-ai': '🤝', 'fireworks-ai': '🎆',

    # AI/ML Libraries
    'pytorch': '🔥', 'tensorflow': '🧠', 'jax': '🔢',
    'sklearn': '📊', 'pandas': '🐼', 'numpy': '🔢',
    'scipy': '📐', 'matplotlib': '📈', 'plotly': '📊',

    # Testing
    'jest': '🃏', 'vitest': '⚡', 'pytest': '🧪', 'playwright': '🎭',
    'cypress': '🌲', 'mocha': '☕', 'testing-library': '🧪',

    # Build Tools
    'vite': '⚡', 'webpack': '📦', 'esbuild': '📦', 'rollup': '📜',
    'parcel': '📦', 'turborepo': '🚀', 'nx': '📐', 'lerna': '🐉',
    'pnpm': '📦', 'bun': '🍞', 'deno': '🦕',

    # Mobile
    'react-native': '📱', 'flutter': '🐦', 'swift': '🍎', 'kotlin': '🤖',
    'capacitor': '🔌', 'tauri': '🦀', 'electron': '⚛️',

    # Styling
    'tailwindcss': '💨', 'shadcn': '🎨', 'radix': '📐', 'chakra': '⚡',
    'material-ui': '🎨', 'ant-design': '🐜', 'styled-components': '💅', 'emotion': '👩‍🎤',

    # API & Data Transfer
    'graphql': '◈', 'trpc': '🔷', 'grpc': '📡', 'websocket': '🔌', 'rest': '🌐',

    # Auth
    'auth0': '🔐', 'clerk': '👤', 'nextauth': '🔑', 'lucia': '🌙',
    'passport': '🛂', 'supabase-auth': '🔐', 'firebase-auth': '🔥',

    # Validation
    'zod': '✅', 'yup': '✔️', 'joi': '🃏', 'valibot': '🤖', 'arktype': '🏛️',

    # Observability
    'sentry': '🐛', 'datadog': '🐕', 'newrelic': '📊', 'grafana': '📈',
    'posthog': '🦔', 'mixpanel': '📊', 'amplitude': '📈',
    'langfuse': '🔍', 'langsmith': '🔧',

    # State Management
    'redux': '🔄', 'zustand': '🐻', 'jotai': '👻', 'recoil': '🔵',
    'mobx': '🔮', 'tanstack-query': '🔄', 'swr': '🔄',

    # CMS
    'contentful': '📝', 'sanity': '📄', 'strapi': '🚀', 'payload': '📦',
    'directus': '📂', 'ghost': '👻',

    # Message Queues
    'kafka': '📬', 'rabbitmq': '🐰', 'bullmq': '🐂', 'celery': '🥬',
    'inngest': '⚡', 'trigger-dev': '⏰',
}


COMPONENT_ICONS = {
    'chrome-extension': '🧩', 'vscode-extension': '💻', 'web-frontend': '🌐',
    'mobile-app': '📱', 'desktop-app': '🖥️', 'api-server': '⚙️',
    'graphql-api': '◈', 'websocket-server': '🔌', 'ml-pipeline': '🧠',
    'data-ingestion': '📥', 'knowledge-graph': '🕸️', 'rag-system': '🔍',
    'kubernetes': '☸️', 'docker-compose': '🐳', 'ci-cd-pipeline': '🔄',
    'cli-tool': '⌨️', 'sdk-library': '📚', 'mcp-server': '🔗', 'agent-system': '🤖',
}


CONCEPT_ICONS = {
    # Architecture
    'microservices': '🔀', 'monorepo': '📦', 'serverless': '☁️',
    'event-driven': '📡', 'clean-architecture': '🏗️',

    # Code Quality
    'testing': '🧪', 'linting': '✨', 'typescript-strict': '💙',
    'ci-cd': '🔄', 'documentation': '📚',

    # Design Patterns
    'dependency-injection': '💉', 'factory-pattern': '🏭', 'singleton': '1️⃣',
    'observer': '👁️', 'repository-pattern': '📦',

    # Modern Practices
    'api-first': '🔌', 'type-safety': '💙', 'immutability': '🔒',
    'functional': 'λ', 'reactive': '🔄',

    # Security
    'authentication': '🔐', 'authorization': '🛡️', 'encryption': '🔒',
    'input-validation': '✅',

    # Performance
    'caching': '💾', 'optimization': '🚀', 'async-patterns': '⚡', 'streaming': '🌊',

    # Orchestration
    'graph-orchestration': '📊', 'hierarchical-orchestration': '🌳',
    'swarm-orchestration': '🐝', 'pipeline-orchestration': '➡️',
}


# =============================================================================
# CATEGORY PURPOSE MAPPING
# =============================================================================

CATEGORY_PURPOSES = {
    'ai-agent': 'AI agent orchestration',
    'scientific': 'scientific workflows',
    'data-science': 'data science & analytics',
    'web-app': 'web application',
    'cli-tool': 'command-line tasks',
    'api': 'API services',
    'mobile': 'mobile experience',
    'infrastructure': 'infrastructure management',
    'data': 'data processing',
    'ml': 'machine learning',
    'rag': 'retrieval-augmented generation',
    'browser-extension': 'browser functionality',
    'library': 'reusable code library',
}


# =============================================================================
# DOMAIN HINTS (for summary generation)
# =============================================================================

DOMAIN_HINTS = {
    # AI/LLM
    'coscientist': 'scientific research',
    'langchain': 'LLM orchestration',
    'langgraph': 'graph-based agents',
    'crewai': 'agent teams',
    'autogen': 'conversational agents',
    'anthropic': 'Claude AI integration',
    'openai': 'GPT integration',
    'huggingface': 'ML models',

    # Cloud & Data
    'cloudflare': 'edge computing',
    'bigquery': 'data analytics',
    'aws': 'cloud infrastructure',
    'gcp': 'cloud services',
    'azure': 'cloud platform',
    'supabase': 'data management',
    'neon': 'serverless postgres',
    'postgresql': 'data storage',
    'elasticsearch': 'search',
    'pinecone': 'vector search',
    'chromadb': 'embeddings',
    'neo4j': 'graph database',
    'falkordb': 'GraphRAG database',
    'surrealdb': 'multi-model database',
    'duckdb': 'embedded analytics',
    'lancedb': 'multimodal vectors',
    'graphiti': 'knowledge graphs',
    'mem0': 'AI memory layer',

    # External Data Sources
    'pubmed': 'biomedical research',
    'arxiv': 'physics/CS preprints',
    'semantic-scholar': 'academic literature',
    'wikipedia': 'knowledge base',
    'github-api': 'code repositories',

    # Preprint Servers
    'biorxiv': 'biology preprints',
    'medrxiv': 'health sciences preprints',
    'chemrxiv': 'chemistry preprints',
    'eartharxiv': 'earth science preprints',
    'socarxiv': 'social science preprints',
    'psyarxiv': 'psychology preprints',
    'techrxiv': 'engineering preprints',
    'ssrn': 'social science/economics',
    'zenodo': 'open research data',

    # Web
    'react-native': 'cross-platform mobile',
    'nextjs': 'web application',
    'fastapi': 'API services',
    'graphql': 'data querying',
}
