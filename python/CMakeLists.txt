cmake_minimum_required()
project(my_bittorrent LANGUAGES C)
add_compile_options(-std=c99 -ljansson -Wall -Werror -Wextra -pedantic -g)


add_custom_target(check
    COMMAND ${CMAKE_SOURCE_DIR}/tests/init_test.sh
    )

