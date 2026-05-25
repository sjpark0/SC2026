./scripts/submit.sh submit init-engine --source-folder /home/sjpark/SC2026/SCCLIPipeline/Server/Test --target-folder /home/sjpark/SC2026/SCCLIPipeline/Server/output_6
./scripts/submit.sh submit extract-video-frame --source-folder /home/sjpark/SC2026/SCCLIPipeline/Server/Test --target-folder /home/sjpark/SC2026/SCCLIPipeline/Server/output_6 --start-frame 1 --finish-frame 3
./scripts/submit.sh submit build-param --source-folder /home/sjpark/SC2026/SCCLIPipeline/Server/Test --target-folder /home/sjpark/SC2026/SCCLIPipeline/Server/output_6 --param-frame 1
./scripts/submit.sh submit build-layer --source-folder /home/sjpark/SC2026/SCCLIPipeline/Server/Test --target-folder /home/sjpark/SC2026/SCCLIPipeline/Server/output_6 --factor 4 --start-frame 1 --finish-frame 3

