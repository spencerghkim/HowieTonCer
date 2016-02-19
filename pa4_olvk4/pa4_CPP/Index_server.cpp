#include "Index_server.h"

#include <cassert>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <pthread.h>
#include <sstream>
#include <math.h>
#include <utility>
#include <algorithm>
#include <cmath>

#include "mongoose.h"

using std::cerr;
using std::cout;
using std::endl;
using std::ifstream;
using std::ostream;
using std::ostringstream;
using std::stringstream;
using std::string;
using std::vector;
using std::for_each;
using std::pair;
using std::map;
using std::sort;

ifstream infile;

namespace {
    int handle_request(mg_connection *);
    int get_param(const mg_request_info *, const char *, string&);
    string get_param(const mg_request_info *, const char *);
    string to_json(const vector<Query_hit>&);

    ostream& operator<< (ostream&, const Query_hit&);
}

pthread_mutex_t mutex;

// Runs the index server on the supplied port number.
void Index_server::run(int port)
{
    // List of options. Last element must be NULL
    ostringstream port_os;
    port_os << port;
    string ps = port_os.str();
    const char *options[] = {"listening_ports",ps.c_str(),0};

    // Prepare callback structure. We have only one callback, the rest are NULL.
    mg_callbacks callbacks;
    memset(&callbacks, 0, sizeof(callbacks));
    callbacks.begin_request = handle_request;

    // Initialize the global mutex lock that effectively makes this server
    // single-threaded.
    pthread_mutex_init(&mutex, 0);
    // pthread_mutex_init(&another_mutex, 1);

    // Start the web server
    mg_context *ctx = mg_start(&callbacks, this, options);
    if (!ctx) {
        cerr << "Error starting server." << endl;
        return;
    }

    pthread_exit(0);
}

// Load index data from the file of the given name.
void Index_server::init(ifstream& infile)
{
    // variables used for each line of indexfile
    double idf;
    string word;
    int total_num_occur;
    
    // variables used per document occurrence
    int docID, docID_num_occur;
    double docID_norm_fac; //before sqrt

    while(infile >> word >> idf >> total_num_occur){
        int count = 0;
        while(count < total_num_occur){
            infile >> docID >> docID_num_occur >> docID_norm_fac;

            // calculate weight
            double weight = double(docID_num_occur)*idf/sqrt(docID_norm_fac);
            doc_weights_map[docID][word] = weight;

            // add docID to set of doc IDs
            word_map[word].docIDs.push_back(docID);
            count += docID_num_occur;
        }

        // sort vector of docIDs
        sort(word_map[word].docIDs.begin(), word_map[word].docIDs.end()); 
        word_map[word].idf = idf;
    }
    cout << "Init finished" << endl;


    // Sanity checks

    // for_each(doc_weights_map.begin(), doc_weights_map.end(), [](pair<int, doc_vector_t> pair){
    //     cout << "docid: " << pair.first << ", weight vector: ";
    //     cout << " size : " << pair.second.size() << " ";
    //     for_each(pair.second.begin(), pair.second.end(), [](std::pair<string, double> pair2){
    //         cout << pair2.second << " ";
    //     });
    //     cout << endl;
    // });



    // Load stopwords
    ifstream stop_words_file;
    stop_words_file.open("english.stop");
    if(!stop_words_file.is_open()){
        cerr << "Stop Words file failed to open" << endl;
        exit(1);
    }
    string tmp_word;
    while(stop_words_file >> tmp_word){
        stop_words.insert(tmp_word);
    }



    // vector<Query_hit> hits;
    // process_query("sushi roll roll", hits);
    // process_query("tofu sushi roll", hits);

}



// Search the index for documents matching the query. The results are to be
// placed in the supplied "hits" vector, which is guaranteed to be empty when
// this method is called.
void Index_server::process_query(const string& query, vector<Query_hit>& hits)
{
    cout << "Processing query '" << query << "'" << endl;

    string query_copy = query;

    // remove garbage characters from query
    query_copy.erase(remove_if(query_copy.begin(), query_copy.end(), 
            [](char c){return !isalnum(c) && !isspace(c);}), query_copy.end());

    // convert query to lowercase
    for(char &c : query_copy){
        c = tolower(c);
    }

    // load query doc with terms and their counts
    map<string, int> query_doc;
    stringstream ss;
    ss << query_copy;
    string word;
    while(ss >> word){
        // skip if we are reading a stopword
        if(stop_words.find(word) != stop_words.end()){
            continue;
        }

        query_doc[word]++;
    }

    // calculate docID_norm_fac for this "document"
    double norm_factor = 0;
    for(auto &pair : query_doc){
        norm_factor += word_map[pair.first].idf * word_map[pair.first].idf
                    * double(pair.second) * double(pair.second);
    }


    // fill query weights "vector"
    doc_vector_t query_weights;
    for_each(query_doc.begin(), query_doc.end(), [&](map<string, int>::value_type pair){ 
        double weight = double(pair.second) * word_map[pair.first].idf / sqrt(norm_factor);
        query_weights[pair.first] = weight;
    });


    // find all docs that contain any word in Q
    vector<int> uniq_docs;
    for(auto &pair : query_doc){
        for(int i=0; i<word_map[pair.first].docIDs.size(); i++){
            uniq_docs.push_back(word_map[pair.first].docIDs[i]);
        }
    }
    sort(uniq_docs.begin(), uniq_docs.end());
    auto it = std::unique(uniq_docs.begin(), uniq_docs.end());
    uniq_docs.resize( std::distance(uniq_docs.begin(),it) );

    // Sanity check
    cout << "unique docids: \n";
    for_each(uniq_docs.begin(), uniq_docs.end(), [](int i){
        cout << i << " ";
    });
    cout << endl;


    // now find best matches

    // calculate query denominator portion
    double query_norm_factor = 0;
    for(auto &pair : query_weights){
        query_norm_factor += pair.second * pair.second;
    }
    for(int &i : uniq_docs){
        // sim_tfidf is numerator
        double sim_tfidf = 0;
        for(auto &pair : query_weights){
            // if doc weight container does not have anything for a given
            // string, then we multiply by 0
            sim_tfidf += pair.second * doc_weights_map[i][pair.first];
        }

        // calculate doc denominator portion
        double doc_norm_factor = 0;
        for(auto &pair : doc_weights_map[i]){
            doc_norm_factor += pair.second * pair.second;
        }

        double sim_norm_factor = sqrt(query_norm_factor * 
            doc_norm_factor);

        double result = sim_tfidf / sim_norm_factor;
    
        // add to hits
        stringstream hue;
        hue.str("");
        hue << i;
        hits.emplace_back(hue.str(), result);

        cout << "document " << i << " has score " << result << endl;
    }

    // sort hits by score
    struct compare{
        bool operator()(const Query_hit &a, const Query_hit &b) const{
            return a.score >= b.score;
        }
    } comp;
    sort(hits.begin(), hits.end(), comp);
    

    // trash

    // vector<int> v;
    // for(auto &pair : query_doc){
    //     auto secondBegin = word_map[pair.first].docIDs.begin();
    //     auto secondEnd = word_map[pair.first].docIDs.end();
    //     auto it = std::set_union(v.begin(), v.end(), 
    //         secondBegin, secondEnd, v.begin());
    //     v.resize(it-v.begin());
    // }
}

namespace {
    int handle_request(mg_connection *conn)
    {
        const mg_request_info *request_info = mg_get_request_info(conn);

        if (!strcmp(request_info->request_method, "GET") && request_info->query_string) {
            // Make the processing of each server request mutually exclusive with
            // processing of other requests.

            // Retrieve the request form data here and use it to call search(). Then
            // pass the result of search() to to_json()... then pass the resulting string
            // to mg_printf.
            string query;
            if (get_param(request_info, "q", query) == -1) {
                // If the request doesn't have the "q" field, this is not an index
                // query, so ignore it.
                return 1;
            }

            vector<Query_hit> hits;
            Index_server *server = static_cast<Index_server *>(request_info->user_data);

            pthread_mutex_lock(&mutex);
            server->process_query(query, hits);
            pthread_mutex_unlock(&mutex);

            string response_data = to_json(hits);
            int response_size = response_data.length();

            // Send HTTP reply to the client.
            mg_printf(conn,
                      "HTTP/1.1 200 OK\r\n"
                      "Content-Type: application/json\r\n"
                      "Content-Length: %d\r\n"
                      "\r\n"
                      "%s", response_size, response_data.c_str());
        }

        // Returning non-zero tells mongoose that our function has replied to
        // the client, and mongoose should not send client any more data.
        return 1;
    }

    int get_param(const mg_request_info *request_info, const char *name, string& param)
    {
        const char *get_params = request_info->query_string;
        size_t params_size = strlen(get_params);

        // On the off chance that operator new isn't thread-safe.
        pthread_mutex_lock(&mutex);
        char *param_buf = new char[params_size + 1];
        pthread_mutex_unlock(&mutex);

        param_buf[params_size] = '\0';
        int param_length = mg_get_var(get_params, params_size, name, param_buf, params_size);
        if (param_length < 0) {
            return param_length;
        }

        // Probably not necessary, just a precaution.
        param = param_buf;
        delete[] param_buf;

        return 0;
    }

    // Converts the supplied query hit list into a JSON string.
    string to_json(const vector<Query_hit>& hits)
    {
        ostringstream os;
        os << "{\"hits\":[";
        vector<Query_hit>::const_iterator viter;
        for (viter = hits.begin(); viter != hits.end(); ++viter) {
            if (viter != hits.begin()) {
                os << ",";
            }

            os << *viter;
        }
        os << "]}";

        return os.str();
    }

    // Outputs the computed information for a query hit in a JSON format.
    ostream& operator<< (ostream& os, const Query_hit& hit)
    {
        os << "{" << "\"id\":\"";

        // int id_size = hit.id > 0 ? (int) log10 ((double) hit.id) + 1 : 1;
        // int id_size = strlen(hit.id);
        int id_size = hit.id.size();
        for (int i = 0; i < id_size; i++) {
            if (hit.id[i] == '"') {
                os << "\\";
            }
            os << hit.id[i];
            // os << hit.id;
        }
        return os << "\"," << "\"score\":" << hit.score << "}";
    }
}
