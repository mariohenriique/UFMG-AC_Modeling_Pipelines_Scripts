from tkinter import filedialog,messagebox
from functions import *
from Bio import Entrez 
import tkinter as tk
import pandas as pd
import logging
import time

def configure_entrez(default_api_key='', default_email=''):
    """
    Configures the credentials for NCBI Entrez.

    Prompts the user to provide the NCBI Entrez settings and sets them.
    The user can provide the API key and associated email. If not provided,
    default values will be used.

    Parameters:
    default_api_key (str): Default API key for NCBI Entrez.
    default_email (str): Default email for NCBI Entrez.
    """
    # Prompt the user to enter the API key
    api_key = input(f"Por favor, insira a sua chave da API do NCBI Entrez: ")

    # Prompt the user to enter their email
    email = input(f"Por favor, insira o seu e-mail para uso com o NCBI Entrez: ")

    # Use default values if the user does not provide them
    if not api_key:
        api_key = default_api_key
        logging.info("Usando chave da API padrão do NCBI Entrez.") # Log the use of the default API key
    if not email:
        email = default_email
        logging.info("Usando e-mail padrão do NCBI Entrez.") # Log the use of the default API key

    # Set the credentials for Entrez
    Entrez.api_key = api_key
    Entrez.email = email

    # Log the configured settings
    logging.info(f"Configurações do NCBI Entrez definidas. Chave da API: {api_key}, E-mail: {email}")

    print("Configurações do NCBI Entrez definidas com sucesso!")

def search_NCBI(search_for, max_retries=3):
    """
    Performs a search in NCBI using the specified term.

    Parameters:
    search_for (str): The term to be searched.
    max_retries (int): Maximum number of query attempts.

    Returns:
    dict: Search result in dictionary format.
    """
    # Loop for the number of retries allowed
    for tentativa in range(max_retries + 1):
        try:
            # Perform the search in the 'taxonomy' database using the specified term
            handle = Entrez.esearch(db='taxonomy', term=search_for)
            result = Entrez.read(handle)  # Read the result from the search handle
            handle.close()  # Close the handle after reading the result
            return result  # Return the search result
        except Exception as e:
            # Log an error if the search fails
            logging.error(f"Erro ao realizar a busca no NCBI para '{search_for}' na tentativa {tentativa+1}: {e}")
            # If this was the last attempt, return None
            if tentativa == max_retries:
                return None

def efetch_NCBI(efetch_for, max_retries=3):
    """
    Retrieves data from NCBI using the specified term.

    Parameters:
    efetch_for (str): The term to be fetched.
    max_retries (int): Maximum number of query attempts.

    Returns:
    dict: Fetch result in dictionary format.
    """
    # Loop for the number of retries allowed
    for tentativa in range(max_retries + 1):
        try:
            # Perform the fetch in the 'taxonomy' database using the specified term
            stream = Entrez.efetch(db='taxonomy', id=efetch_for)
            result = Entrez.read(stream)  # Read the result from the fetch stream
            stream.close()  # Close the stream after reading the result
            return result  # Return the fetch result
        except Exception as e:
            # Log an error if the fetch fails
            logging.error(f"Erro ao realizar a busca no NCBI para '{efetch_for}' na tentativa {tentativa + 1}: {e}")
            # If this was the last attempt, return None
            if tentativa == max_retries:
                return None

def search_tax_id(scientific_name, max_retries=3):
    """
    Searches for the taxonomy ID of a given scientific name.

    Parameters:
    scientific_name (str): The scientific name of the species.
    max_retries (int): The maximum number of retry attempts for the query (default is 3).

    Returns:
    str: The taxonomy ID of the species, or None if not found or an error occurs.
    """
    # Perform a search in NCBI using the provided scientific name
    result = search_NCBI(scientific_name, max_retries)
    
    if result:
        # Join the list of IDs into a single string
        txid = ','.join(result['IdList'])
        if txid:
            logging.info(f"ID de taxonomia obtido com sucesso para '{scientific_name}'.")
            return txid  # Return the taxonomy ID if found
        else:
            logging.warning(f"Nome científico '{scientific_name}' não encontrado na pesquisa.")
            return None  # Return None if no IDs were found
    else:
        logging.error(f"Erro ao buscar ID de taxonomia para '{scientific_name}'.")
        return None  # Return None if there was an error in the search

def fetch_tax_info(txid, max_retries=3):
    """
    Fetches taxonomy information for a given taxonomy ID.

    Parameters:
    txid (str): The taxonomy ID of the species.
    max_retries (int): The maximum number of retry attempts for the query (default is 3).

    Returns:
    tuple: A tuple containing the scientific name, the taxonomic rank,
           and the ID of the higher taxon. If an error occurs, returns (None, None, None).
    """
    # Fetch the taxonomy record using the provided taxonomy ID
    record = efetch_NCBI(txid, max_retries)
    
    if record:
        # Extract scientific name, taxonomic rank, and superior taxon ID
        name = record[0]['ScientificName']
        rank = record[0]['Rank']
        taxid_sup_rank = record[0]['LineageEx'][-1]['TaxId']
        logging.info(f"Informações de taxonomia obtidas com sucesso para '{name}'.")
        return name, rank, taxid_sup_rank  # Return the extracted information as a tuple
    else:
        logging.error(f"Erro ao obter informações de taxonomia para o ID '{txid}'.")
        return None, None, None  # Return None values if the fetch fails

def get_taxonomy_id(scientific_name, max_retries=3):
    """
    Retrieves taxonomy information for a given scientific name.

    Parameters:
    scientific_name (str): The scientific name of the species.
    max_retries (int): The maximum number of retry attempts for the query (default is 3).

    Returns:
    tuple: A tuple containing the scientific name, the taxonomy ID, the taxonomic rank, 
           and the ID of the higher taxon. If the scientific name is not found, 
           the tuple includes a string with the name of the species that was not found.
    """
    errors = ''  # Initialize an empty string to store errors
    # Search for the taxonomy ID using the provided scientific name
    txid = search_tax_id(scientific_name, max_retries)
    
    if txid:
        # Fetch taxonomic information using the found taxonomy ID
        name, rank, taxid_sup_rank = fetch_tax_info(txid, max_retries)
        time.sleep(0.1)  # Sleep for a short duration to avoid overwhelming the server
        return name, txid, rank, taxid_sup_rank, errors  # Return the retrieved information
    else:
        errors = scientific_name  # Store the scientific name in errors if not found
        time.sleep(0.1)  # Sleep for a short duration
        return None, None, None, None, errors  # Return None values and the error message

def salvar_arquivo(extensao='.csv'):
    """
    Opens a file selection dialog for the user to choose the location and name of a CSV file.

    Parameters:
    extensao (str): The default file extension for the saved file (default is '.csv').

    Returns:
    str: The full path of the file to be saved. If the user cancels the dialog, an empty string is returned.
    """
    print("Abrindo caixa de seleção para salvar o arquivo. Por favor, verifique se a janela não está oculta.")
    
    # Create an instance of the main Tkinter window and hide it
    root = tk.Tk()
    root.withdraw()

    # Display a file dialog for the user to choose the save location and file name
    caminho_arquivo = filedialog.asksaveasfilename(
        defaultextension=extensao,  # Default file extension
        # filetypes=[("Arquivos CSV", "*.csv")],  # Uncomment if you want to restrict file types
        title="Salvar Arquivo"  # Title of the dialog window
    )
    return caminho_arquivo  # Return the full path of the file to be saved

def selecionar_arquivo():
    """
    Opens a file selection dialog for the user to choose a CSV file.

    Returns:
    str: The full path of the selected file. If the user cancels the dialog, an empty string is returned.
    """
    print("Abrindo caixa de seleção de arquivo. Por favor, verifique se a janela não está oculta.")

    # Create an instance of the main Tkinter window and hide it
    root = tk.Tk()
    root.withdraw()

    # Display a file dialog for the user to choose a file
    arquivo_csv = filedialog.askopenfilename(
        title="Select a file",
        filetypes=[("File", "*.*")],
        multiple=False
    )

    # Return the path of the selected file
    return arquivo_csv

def ler_arquivo_csv():
    """
    Reads the selected CSV file and checks for the presence of the 'scientificName' column.

    Returns:
    DataFrame: The DataFrame containing the data from the CSV file if the 'scientificName' column is present; 
               otherwise, returns None.
    """
    # Prompt the user to select a CSV file
    arquivo_csv = selecionar_arquivo()
    
    try:
        logging.info(f"Lendo o arquivo CSV: {arquivo_csv}")  # Log the CSV file being read
        df = pd.read_csv(arquivo_csv)  # Read the selected CSV file into a DataFrame

        # Check if 'scientificName' column is present
        if 'scientificName' not in df.columns:
            logging.error(f"O arquivo selecionado {arquivo_csv} não contém a coluna 'scientificName'.")
            messagebox.showerror("Erro", "O arquivo selecionado não contém a coluna 'scientificName'. Por favor, selecione outro arquivo.")
            # Recursively call the function to select a new file if the column is missing
            return ler_arquivo_csv()
        else:
            logging.info(f"Coluna 'scientificName' encontrada no arquivo {arquivo_csv}.")
            return df  # Return the DataFrame if the column is present
    except Exception as e:
        logging.error(f"Erro ao ler o arquivo CSV: {e}")  # Log any error that occurs
        messagebox.showerror("Erro", f"Erro ao ler o arquivo CSV: {e}")  # Show an error message

def get_children(tax_hierar, nome_cientifico_col='scientificName', filhos_col='index_filho', root=any, arvore={}):
    """
    Recursive function to obtain the children of a node in the taxonomic hierarchy.

    Parameters:
    tax_hierar (DataFrame): The DataFrame containing the taxonomic hierarchy.
    nome_cientifico_col (str): The name of the column that contains the scientific names of the taxa (default is 'scientificName').
    filhos_col (str): The name of the column that contains the indices of the children for each taxon (default is 'index_filho').
    root (any): The root node to start building the tree (default is any value).
    arvore (dict): The dictionary representing the tree structure (default is an empty dictionary).

    Returns:
    None
    """
    # Retrieve the indices of children for the specified root in the taxonomic hierarchy
    indices_filho = tax_hierar.loc[tax_hierar[nome_cientifico_col] == root, filhos_col].values
    
    if len(indices_filho) > 0:  # Check if there are any children
        indices_filho = indices_filho[0]  # Get the first (and usually only) value
        
        if pd.notna(indices_filho):  # Ensure the value is not NaN
            indices_filho = indices_filho.split(',')  # Split the indices into a list
            indices_filho = [int(i) for i in indices_filho]  # Convert indices to integers
            
            # Get the scientific names of the children using the retrieved indices
            filhos_raiz = tax_hierar.loc[indices_filho, nome_cientifico_col]
            arvore[root] = {filho for filho in filhos_raiz}  # Store children in the tree under the root

            # Recursively add children to the corresponding root in the tree dictionary
            for filho in filhos_raiz:
                get_children(tax_hierar, root=filho, arvore=arvore)

def construir_arvore_taxonomica(tax_hierar, nome_cientifico_col='scientificName', filhos_col='index_filho', root=any):
    """
    Constructs a taxonomic tree from the provided taxonomic hierarchy data.

    Parameters:
    tax_hierar (DataFrame): The DataFrame containing the taxonomic hierarchy.
    nome_cientifico_col (str): The name of the column that contains the scientific names of the taxa (default is 'scientificName').
    filhos_col (str): The name of the column that contains the indices of the children for each taxon (default is 'index_filho').
    root (any): The root node or a list of root nodes to start building the tree (default is any value).

    Returns:
    dict: A dictionary representing the taxonomic tree.
    """
    # Initialize the tree
    arvore = {}
    
    # Initialize the tree with the root 'Eukaryota'
    arvore['Eukaryota'] = {'Metazoa', 'Viridiplantae'}

    # Call the get_children function to build the tree from the provided roots
    for raiz in root:
        get_children(tax_hierar, root=raiz, arvore=arvore)

    return arvore

def arvore_para_newick(arvore, no_raiz):
    """
    Converts a tree represented as a dictionary into Newick format.

    Parameters:
    arvore (dict): The dictionary representing the tree.
    no_raiz (str): The root node of the tree.

    Returns:
    str: The Newick representation of the tree.

    This function recursively traverses the tree structure, converting each node and its children
    into the Newick format, which is commonly used to represent phylogenetic trees. The output
    consists of nested parentheses, indicating the relationships between taxa, followed by the 
    names of the taxa.
    """
    if no_raiz not in arvore:
        return no_raiz
    else:
        filhos = arvore[no_raiz]
        newick = "("
        # Recursively convert the children into Newick format
        for filho in filhos:
            newick += arvore_para_newick(arvore, filho) + ","
        newick = newick[:-1] + ")"  # Remove the last comma and add closing parenthesis
        return newick + no_raiz

# URL of the API for taxonomic information
url_api = 'http://bioinfo.icb.ufmg.br/cgi-bin/taxallnomy/taxallnomy_multi.pl'

# A string specifying the ranks for the Darwin Core (DwC) classification standard.
rank_dwc = 'Kingdom, Phylum, Class, Order, Superfamily, Family, Subfamily, Genus, Subgenus, Species'

