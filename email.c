#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <pthread.h>
#include <time.h>

#define MAX_EMAILS 100
#define MAX_SUBJECT_LENGTH 100
#define MAX_BODY_LENGTH 400
#define MAX_KEYWORDS 10
#define MAX_KEYWORD_LENGTH 50
#define CHUNK_SIZE 50

struct Email {
    char subject[MAX_SUBJECT_LENGTH];
    char body[MAX_BODY_LENGTH];
    int priority;
};

struct ThreadArgs {
    char* keyword;
    struct Email* email;
};

int is_high_priority(const char* subject, const char* body, const char* keyword) {
    return strstr(subject, keyword) || strstr(body, keyword);
}

int total_threads = 0;

void* search_keyword_in_email(void* arg) {
    struct ThreadArgs* args = (struct ThreadArgs*)arg;
    char* keyword = args->keyword;
    struct Email* email = args->email;

    if (is_high_priority(email->subject, email->body, keyword)) {
        email->priority = 1;
    }

    total_threads++;

    return NULL;
}

void print_emails_by_priority(struct Email* emails, int num_emails) {
    for (int i = 0; i < num_emails - 1; ++i) {
        for (int j = 0; j < num_emails - i - 1; ++j) {
            if (emails[j].priority < emails[j + 1].priority) {
                // Swap emails
                struct Email temp = emails[j];
                emails[j] = emails[j + 1];
                emails[j + 1] = temp;
            }
        }
    }

    printf("Emails sorted by priority:\n");
    for (int i = 0; i < num_emails; ++i) {
        printf("Email subject: %s (Priority: %s)\n", emails[i].subject,
               emails[i].priority ? "High" : "Normal");
    }
}

int main() {
    int num_emails;
    printf("Enter the number of emails: ");
    scanf("%d", &num_emails);
    printf("Number of emails: %d\n", num_emails);

    struct Email emails[MAX_EMAILS];
    char* keywords[MAX_KEYWORDS];
    int num_keywords;

    printf("Enter the number of keywords: ");
    scanf("%d", &num_keywords);
    printf("Enter keywords (one per line):\n");
    getchar();
    for (int i = 0; i < num_keywords; ++i) {
        keywords[i] = (char*)malloc(MAX_KEYWORD_LENGTH * sizeof(char));
        if (keywords[i] == NULL) {
            perror("Memory allocation failed");
            exit(EXIT_FAILURE);
        }
        if (fgets(keywords[i], MAX_KEYWORD_LENGTH, stdin) == NULL) {
            perror("Error reading keyword");
            exit(EXIT_FAILURE);
        }
        if (keywords[i][strlen(keywords[i]) - 1] == '\n') {
            keywords[i][strlen(keywords[i]) - 1] = '\0';
        }
    }

    struct timespec start, end;

    printf("Enter email details:\n");
    for (int i = 0; i < num_emails; ++i) {
        printf("Enter email subject %d: ", i + 1);
        scanf(" %[^\n]", emails[i].subject);
        printf("Enter email body %d (up to 400 characters): ", i + 1);
        getchar();
        fgets(emails[i].body, sizeof(emails[i].body), stdin);
        if (emails[i].body[strlen(emails[i].body) - 1] == '\n') {
            emails[i].body[strlen(emails[i].body) - 1] = '\0';
        }

        pthread_t threads[MAX_KEYWORDS];
        struct ThreadArgs args[MAX_KEYWORDS];
        clock_gettime(CLOCK_REALTIME, &start);
        for (int j = 0; j < num_keywords; ++j) {
            args[j].keyword = keywords[j];
            args[j].email = &emails[i];
            pthread_create(&threads[j], NULL, search_keyword_in_email, &args[j]);
        }

        for (int j = 0; j < num_keywords; ++j) {
            pthread_join(threads[j], NULL);
        }
    }

    clock_gettime(CLOCK_REALTIME, &end);

    double total_time_ms = (end.tv_sec - start.tv_sec) * 1000.0 +
                           (end.tv_nsec - start.tv_nsec) / 1000000.0;

    print_emails_by_priority(emails, num_emails);

    printf("Total number of threads made: %d\n", total_threads);

    printf("Total time taken: %.2f milliseconds\n", total_time_ms);

    for (int i = 0; i < num_keywords; ++i) {
        free(keywords[i]);
    }

    return 0;
}