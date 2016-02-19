#ifndef INDEXER_H
#define INDEXER_H

#include <iosfwd>
#include <set>
#include <map>
#include <vector>
#include <string>

class Indexer {
public:
    Indexer();
    void index(std::ifstream& content, std::ostream& outfile);
private:
	// use a set since total # of stopwords is not very large...
	std::set<std::string> stop_words;
	
	struct WordData{
		// docID -> term freq of word in doc
		std::map<int, int> docid_map;
		double idf;
		int total_num_occur;
	};
	// again, use an (ordered) map since captions file is quite small
	// if we had a much larger captions file we would use an unordered_map
	std::map<std::string, WordData> word_map;

	struct DocData{
		DocData(std::string d) : doc_data(d) { }
		double normalization_factor;
		std::string doc_data;
	};
	std::vector<DocData> docs_c;
};

#endif
