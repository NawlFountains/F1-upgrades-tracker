import os
import requests

def download_pdf(pdf_url: str, output_filename: str | None ="archivo.pdf" ) -> str | None:
    """Download a PDF based on the link and save it as the output_filename in 'upgrades_pdf' folder

    Args:
        pdf_url: url of the PDF to download
        output_filename: filename to store the downloaded PDF as.
    Returns:
        relative path of the downloaded PDF, None if download failed.
    """
    headers = {"User-Agent": "Mozilla/5.0"}
    
    print(f"Downloading from: {pdf_url}")
    response = requests.get(pdf_url, headers=headers, stream=True)
    
    if response.status_code == 200:
        with open(output_filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Download complete, saved as: {output_filename}")
    else:
        print(f"Error downloading pdf: {response.status_code}")
    return output_filename


def get_car_submission_pdf(year: int, gp_name: str) -> str :
    """Download car submission PDF given year and gp_name, saving it and returing it's path

    Args:
        year: year of submission
        gp_name: official name of the gp, e.g: hugarian_grand_prix
    Return:
        relative path (str) of the local downloaded pdf if succesful, None if failed
    """
    filename = f"{year}_{gp_name}_car_presentation_submissions.pdf"
    url = f"https://www.fia.com/system/files/decision-document/{year}_{gp_name}_-_car_presentation_submissions.pdf"
    return download_pdf(url, filename)

if __name__ == "__main__":
    get_car_submission_pdf(2026, 'hungarian_grand_prix')