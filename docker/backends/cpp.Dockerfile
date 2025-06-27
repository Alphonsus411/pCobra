FROM gcc:12-slim
WORKDIR /work
COPY compile_cpp.sh /usr/local/bin/compile_cpp.sh
RUN chmod +x /usr/local/bin/compile_cpp.sh
CMD ["/usr/local/bin/compile_cpp.sh"]
