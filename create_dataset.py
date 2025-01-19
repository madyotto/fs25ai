import os
import json
from datetime import datetime
import argparse
import requests
from bs4 import BeautifulSoup

class FS25DatasetCreator:
    def __init__(self, schema_dir, doc_dir, output_dir):
        self.schema_dir = schema_dir
        self.doc_dir = doc_dir
        self.output_dir = output_dir
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def validate_directories(self):
        if not os.path.exists(self.schema_dir):
            raise ValueError(f"Schema directory not found: {self.schema_dir}")
        if not os.path.exists(self.doc_dir):
            raise ValueError(f"Documentation directory not found: {self.doc_dir}")
    
    def read_file_pairs(self):
        dataset = []
        for filename in os.listdir(self.schema_dir):
            if filename.endswith('.xsd'):
                base_name = filename[:-4]
                xsd_path = os.path.join(self.schema_dir, filename)
                doc_path = os.path.join(self.doc_dir, f"{base_name}.html")
                
                if os.path.exists(doc_path):
                    try:
                        with open(xsd_path, 'r', encoding='utf-8') as xsd_file:
                            xsd_content = xsd_file.read()
                        
                        with open(doc_path, 'r', encoding='utf-8') as doc_file:
                            doc_content = doc_file.read()
                        
                        entry = {
                            "name": base_name,
                            "xsd_content": xsd_content,
                            "document_content": doc_content,
                            "metadata": {
                                "timestamp": datetime.now().isoformat(),
                                "xsd_path": xsd_path,
                                "doc_path": doc_path,
                                "xsd_size": os.path.getsize(xsd_path),
                                "doc_size": os.path.getsize(doc_path)
                            }
                        }
                        dataset.append(entry)
                        print(f"Processed: {base_name}")
                    except Exception as e:
                        print(f"Error processing {base_name}: {str(e)}")
        
        return dataset

    def read_gdn_documentation(self):
        url = "https://gdn.giants-software.com/documentation_i3d.php"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        content = soup.find('div', {'class': 'entry'})
        clean_text = content.get_text(separator='\n', strip=True)
        
        return clean_text

    def create_dataset(self):
        self.validate_directories()
        dataset = self.read_file_pairs()
        i3d_doc = self.read_gdn_documentation()
        
        complete_dataset = {
            "file_pairs": dataset,
            "gdn_i3d_documentation": i3d_doc
        }
        
        output_file = os.path.join(self.output_dir, 'fs25_dataset.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(complete_dataset, f, indent=2)
        
        print(f"\nDataset created successfully!")
        print(f"Total pairs processed: {len(dataset)}")
        print(f"Output saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Create FS25 XSD-Documentation Dataset')
    parser.add_argument('--schema_dir', required=True, help='Directory containing XSD schema files')
    parser.add_argument('--doc_dir', required=True, help='Directory containing documentation XML files')
    parser.add_argument('--output_dir', default='output', help='Output directory for the dataset')
    
    args = parser.parse_args()
    
    creator = FS25DatasetCreator(args.schema_dir, args.doc_dir, args.output_dir)
    creator.create_dataset()

if __name__ == "__main__":
    main()
