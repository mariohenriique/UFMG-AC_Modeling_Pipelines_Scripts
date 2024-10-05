# UFMG-AC_Modeling_Pipelines_Scripts
Scripts e pipelines para padronização de metadados da Coleção Acarológica do CCT-UFMG no formato Darwin Core. Inclui automação de análises de modelagem de distribuição de espécies e processamento de sequências genéticas, facilitando o compartilhamento e a atualização contínua dos dados.

## Pipeline Taxallnomy
The identification of specimens at the lowest taxonomic level is a challenging daily task in several taxonomic collections, and hence data entry for the classification often requires special attention. Data sometimes changes either because researchers examining specimens update their classification, describe them as new species, or because the entire systematics of a group is modified as new phylogenetic analyses are published. These changes introduce data inconsistencies concerning other taxonomical ranks.

TaxonomyDataProcessor is a pipeline written in Python aiming to address these types of errors. The user provides the scientific name or a list of scientific names as input, and the output is a hierarchical database. For example, if the user provides “Onychophora,” the pipeline outputs the higher rank taxon and the query taxon (Metazoa, Onychophora), the unique taxon NCBI identifier (taxonID) of both (33208, 27563), the position in the database of the child and parent, and the taxonID of parent and child.

### Features
#### Reads Input from CSV File:
- Input: CSV file in DarwinCore (DwC) format.
- Data to be searched: A column named “scientificName”.
#### Searches in NCBI Taxonomy:
- Retrieves taxonomic information for scientific names.
#### Appends Data to Database:
- Adds taxon rank, taxonID, and higher taxon to the database.
#### Error Handling with Retries:
- If errors occur during the NCBI search, the process retries up to three times.
#### Queries Taxallnomy API:
- Submits taxonID to the Taxallnomy API to return all higher taxa.
#### Verifies Higher Taxa in Database:
- Ensures higher taxa are present in the database.
#### Constructs Hierarchical Dataframe:
- Outputs a hierarchical database with scientific name, taxon rank, parent taxonID, and child taxonID.
### Key Functions and Components
- configure_entrez(): Configures NCBI Entrez credentials using user input.
- search_NCBI() and efetch_NCBI(): Perform search and fetch operations on the NCBI Entrez database with retry mechanisms.
- search_tax_id(): Searches for the taxonomic ID of a species using its scientific name.
- fetch_tax_info(): Fetches detailed taxonomic information for a given taxonomic ID.
- ler_arquivo_csv(): Reads a CSV file and checks for the presence of the scientificName column.
- get_taxonomy_id(): Retrieves the taxonomic ID and other relevant information for a scientific name.
- get_children() and construir_arvore_taxonomica(): Recursively build the taxonomic tree from the DataFrame.
- arvore_para_newick(): Converts the taxonomic tree to Newick format.
### Usage
#### Prepare Input CSV File:
- Ensure the CSV file is in DarwinCore format and contains a column named “scientificName”.
#### Run the Pipeline:
- Execute the Python script to process the input file and generate the hierarchical database.
#### Output:
- The output is a hierarchical database that includes taxonomic information from the kingdom down to the lowest taxonomic level. This script is designed to process a CSV file containing scientific names of species and construct a taxonomic hierarchy using data retrieved from the NCBI Entrez database and a custom API.


## Mite Data Collection and Scientific Dissemination Website
In order to make data available, correct published information, and promote scientific dissemination about mites, we are developing a website using the Django framework in Python. The site features various pages focused on viewing data about the collection and mite families.

### Features
- Data Visualization: Displays detailed information about the collection and mite families.
- Dynamic Form: Allows data insertion in DwC format, automatically correcting dependent columns. Data can be added manually through the form or via a CSV file.
- Dynamic Factsheets: Each mite family has a dedicated page with general information, diagnoses, images, maps, and genetic data, automatically updated as new records are added or edited in the database.
-Automated Maps and Reports: Continuous generation of maps, reports, and nucleotide sequence alignments, with integration to public data repositories like GenBank and BOLD.
-Access Control: Data modifications are restricted to authorized users who are logged in, ensuring data integrity.

### Technologies Used

- Backend: Python (Django)
- Database: PostgreSQL or MySQL (or any Django-compatible database)
- Frontend: HTML, CSS, JavaScript
- Integration: GenBank, BOLD, CSV, DwC

### Prerequisites
To run the project locally, you will need:

- Python 3.10
- Django 4.2.1
- PostgreSQL or MySQL (or another database)

#### Installation
Follow the steps below to set up the project locally:
```
# Create a virtual environment
python -m venv env

# Activate the virtual environment
source env/bin/activate  # On Linux/macOS
env\Scripts\activate  # On Windows

# Install the dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

### How to Use
- Data Insertion: Use the form provided on the site to add new data to the collection or upload a CSV file in DwC format.
- Dynamic Factsheets: Access dynamic pages with automatically updated information about mite families.
