#ifndef INDEX_SERVER_H
#define INDEX_SERVER_H

#include <iosfwd>
#include <stdint.h>
#include <string>
#include <vector>
#include <set>
#include <map>

struct Query_hit {
    Query_hit(std::string id_, double score_)
        : id(id_), score(score_)
        {}

    std::string id;
    double score;
};

class Index_server {
public:
	using doc_vector_t = std::map<std::string, double>;

    void run(int port);

    // Methods that students must implement.
    void init(std::ifstream& infile);
    void process_query(const std::string& query, std::vector<Query_hit>& hits);

private:

	std::set<std::string> stop_words;
	
	struct WordData{
		std::vector<int> docIDs;
		double idf;
	};

	// again, use an (ordered) map since captions file is quite small
	// if we had a much larger captions file we would use an unordered_map
	std::map<std::string, WordData> word_map;

	// struct DocData{
	// 	// DocData(std::string d) : doc_data(d) { }
	// 	double norm_fac;
	// 	// std::string doc_data;
	// 	std::map<std::string, double> doc_vector;
	// }; 
	// int = docID
	
	std::map<int, doc_vector_t> doc_weights_map;

};

#endif
