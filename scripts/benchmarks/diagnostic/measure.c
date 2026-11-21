#define _DEFAULT_SOURCE
#include <errno.h>
#include <stdio.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <time.h>
#include <unistd.h>

int main(int argc, char **argv) {
    if (argc < 3) return 125;
    struct timespec start, end;
    struct rusage usage;
    int status;
    if (clock_gettime(CLOCK_MONOTONIC, &start)) return 125;
    pid_t pid = fork();
    if (pid < 0) return 125;
    if (pid == 0) {
        execvp(argv[2], &argv[2]);
        perror("execvp");
        _exit(126);
    }
    pid_t waited;
    do { waited = wait4(pid, &status, 0, &usage); } while (waited < 0 && errno == EINTR);
    if (waited < 0 || clock_gettime(CLOCK_MONOTONIC, &end)) return 125;
    FILE *metrics = fopen(argv[1], "w");
    if (!metrics) return 125;
    double seconds = end.tv_sec - start.tv_sec + (end.tv_nsec - start.tv_nsec) / 1e9;
    fprintf(metrics, "%.9f %ld\n", seconds, usage.ru_maxrss);
    if (fclose(metrics)) return 125;
    return WIFEXITED(status) ? WEXITSTATUS(status) : 128 + WTERMSIG(status);
}
