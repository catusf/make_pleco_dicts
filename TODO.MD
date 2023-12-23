TODO
[X] Add suggested item from top 5000 HSK words
[X] Store data in XML/JSON
[X] Extract examples into list
[X] Make Chinese text blue, and từ loại grey
[X] Only include items from top_24k and top_100k
[ ] Use Taiwan MOE dictionary to find opposite words (antonyms)
[ ] Check words that have puntuations at the end

# Steps
[ ] Convert Thienchuu to same format
[ ] Add remaining Thienchuu
[ ] Get list on un-covered items in 75k list

[ ] Add list of HSK: All level
[ ] Lấy danh sách OpenSubstitles 
[ ] Check lenght of definitions, examples and recommedations

BeauttifulSoup

- Find by id

results = soup.find(id="ResultsContainer")

- Find Elements by HTML Class Name

job_elements = results.find_all("div", class_="card-content")

first_elem = results.find("div", class_="card-content")

- Iterate over the elements

for job_element in job_elements:
    title_element = job_element.find("h2", class_="title")
    company_element = job_element.find("h3", class_="company")
    location_element = job_element.find("p", class_="location")
    print(title_element)
    print(company_element)
    print(location_element)
    print()

- Extract Text From HTML Elements


for job_element in job_elements:
    title_element = job_element.find("h2", class_="title")
    company_element = job_element.find("h3", class_="company")
    location_element = job_element.find("p", class_="location")
    print(title_element.text.strip())
    print(company_element.text.strip())
    print(location_element.text.strip())
    print()

- Extract Attributes From HTML Elements

for job_element in python_job_elements:
    # -- snip --
    links = job_element.find_all("a")
    for link in links:
        link_url = link["href"]
        print(f"Apply here: {link_url}\n")

		



