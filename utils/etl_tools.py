import os
import requests
import json
import csv

# Attempt to import pandas, with fallback for Windows Smart App Control (SAC) blocks
try:
    import pandas as pd
    HAS_PANDAS = True
    PANDAS_ERROR = None
except Exception as e:
    pd = None
    HAS_PANDAS = False
    PANDAS_ERROR = str(e)


class ETLTools:

    def __init__(self):
        pass

    def extract_load(self, url: str, output_folder: str, format: str):
        """
        Extracts data from an API (url) and loads it into the desired location (output_folder).

        Args:
            url (str): The API endpoint from which to extract data.
            output_folder (str): The folder where the extracted data will be saved.
            format (str): The format in which to save the extracted data (csv, json, parquet).

        Returns:
            str: A message indicating the success or failure of the operation.
        """
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        output_folder = os.path.join(project_root, output_folder)

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            data = response.json()

            os.makedirs(output_folder, exist_ok=True)
            filename = os.path.join(output_folder, f"extracted_data.{format}")

            results = data.get('results', data)

            if HAS_PANDAS:
                df = pd.json_normalize(results)
                if format == "csv":
                    df.to_csv(filename, index=False)
                elif format == "json":
                    df.to_json(filename, orient="records", lines=True)
                elif format == "parquet":
                    df.to_parquet(filename, index=False)
                else:
                    return f"Unsupported format: {format}"
            else:
                # Fallback using standard library (handles Windows SAC restriction on pandas)
                if format == "json":
                    with open(filename, "w", encoding="utf-8") as f:
                        json.dump(results, f, indent=2)
                elif format == "csv":
                    if isinstance(results, list) and len(results) > 0 and isinstance(results[0], dict):
                        keys = list(results[0].keys())
                        with open(filename, "w", newline="", encoding="utf-8") as f:
                            writer = csv.DictWriter(f, fieldnames=keys)
                            writer.writeheader()
                            writer.writerows(results)
                    else:
                        with open(filename, "w", newline="", encoding="utf-8") as f:
                            writer = csv.writer(f)
                            writer.writerow(["data"])
                            for item in results:
                                writer.writerow([str(item)])
                elif format == "parquet":
                    import pyarrow as pa
                    import pyarrow.parquet as pq
                    table = pa.Table.from_pylist(results)
                    pq.write_table(table, filename)
                else:
                    return f"Unsupported format: {format}"

            return f"Data successfully extracted and saved to {filename}"
        except requests.exceptions.RequestException as e:
            return f"Failed to extract data: {e}"
        except Exception as e:
            return f"Error during extraction/saving: {e}"

    def transform_load_context(self, file_path: str):
        """
        Inspects the file and returns a preview of the top rows to give context to the LLM.

        Args:
            file_path (str): The path to the file containing data to be transformed.

        Returns:
            str: Preview of the top rows or an error message.
        """
        if not os.path.exists(file_path):
            return f"File does not exist: {file_path}"

        file_extension = os.path.splitext(file_path)[1].lower()

        if HAS_PANDAS:
            try:
                if file_extension == ".csv":
                    df = pd.read_csv(file_path)
                elif file_extension == ".json":
                    df = pd.read_json(file_path, lines=True)
                elif file_extension == ".parquet":
                    df = pd.read_parquet(file_path)
                else:
                    return f"Unsupported file format: {file_extension}"
                return str(df.head(3))
            except Exception:
                pass

        # Resilient fallback using standard library & pyarrow
        try:
            if file_extension == ".csv":
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    reader = csv.reader(f)
                    preview = [next(reader, None) for _ in range(4)]
                    preview = [row for row in preview if row is not None]
                    return f"CSV Preview (Header + Top 3 Rows):\n" + "\n".join([str(r) for r in preview])
            elif file_extension == ".json":
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    lines = [f.readline().strip() for _ in range(3)]
                    return f"JSON Preview:\n" + "\n".join([line for line in lines if line])
            elif file_extension == ".parquet":
                import pyarrow.parquet as pq
                table = pq.read_table(file_path)
                return f"Parquet Preview:\n{str(table.schema)}\nTop 3 rows: {table.slice(0, 3).to_pydict()}"
            else:
                return f"Unsupported file format: {file_extension}"
        except Exception as e:
            return f"Error reading file context: {e}"

    def execute_code(self, code: str):
        """
        Executes the provided transformation code and returns the output.

        Args:
            code (str): The Python code to be executed.

        Returns:
            str: Output of the executed code or an error message if execution fails.
        """
        try:
            exec(code)
            return "Code executed successfully."
        except Exception as e:
            return f"Failed to execute code: {e}"


if __name__ == "__main__":
    obj = ETLTools()
    path = os.path.join(os.path.dirname(__file__), "..", "data", "users.csv")
    print(obj.transform_load_context(path))
