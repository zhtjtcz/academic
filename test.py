
'''
import arxiv

search = arxiv.Search(
  query = "NetSD: Remote Access to Integrated SD Cards of Embedded Devices",
  max_results = 1,
  sort_by = arxiv.SortCriterion.Relevance
)

for result in search.results():
  print(result.pdf_url)

search = arxiv.Search(id_list=["1605.08386v1"])
paper = next(search.results())
print(paper.title)
'''
