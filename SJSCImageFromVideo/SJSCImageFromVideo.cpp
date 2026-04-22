// SJSCImageFromVideo.cpp : 이 파일에는 'main' 함수가 포함됩니다. 거기서 프로그램 실행이 시작되고 종료됩니다.
//

#include <iostream>
/*#include "DecoderManager.h"
int main(int argc, char* argv[])
{
    int numDecoder = atoi(argv[1]);
    const char* prefix = argv[2];
    const char* ext = argv[3];
    char** filenames = new char* [numDecoder];
    for (int i = 0; i < numDecoder; i++) {
        filenames[i] = new char[1024];
        sprintf(filenames[i], "%s-%d.%s", prefix, i, ext);
        printf("%s\n", filenames[i]);
    }
    DecoderManager manager;
    //DecoderManagerGPU manager;
    manager.Initialize(numDecoder, filenames, argv[4], 3840, 2160, 0);

    FILE *fp;
    char filename1[1024];
    sprintf(filename1, "%s/input.json", argv[4]);
	fp = fopen(filename1, "w");
    fprintf(fp, "{\n");        
    for(int i=0; i < numDecoder; i++){
        fprintf(fp, "\t  \"Video %d\" : {\n", i);
        fprintf(fp, "\t\t  \"Frame Number\" : %ld,\n", manager.GetNumFrame(i));
        fprintf(fp, "\t\t  \"Frame rate \" : %.03f\n", manager.GetFrameRate(i));
        fprintf(fp, "\t}");
        if(i != numDecoder - 1){
            fprintf(fp, ",");
        }
        fprintf(fp, "\n");
        
    }
    fprintf(fp, "}");
    fclose(fp);
    manager.DoDecoding();

    for (int i = 0; i < numDecoder; i++) {
        delete[]filenames[i];
    }
    delete[]filenames;

    
    return 0;
}*/

#include "etriSCDecoder.h"
#include "DecoderManager.h"
int main(int argc, char* argv[])
{
    int numDecoder = atoi(argv[1]);
    const char* prefix = argv[2];
    const char* ext = argv[3];
    char** filenames = new char* [numDecoder];
    for (int i = 0; i < numDecoder; i++) {
        filenames[i] = new char[1024];
        sprintf(filenames[i], "%s%02d.%s", prefix, i+1, ext);
        printf("%s\n", filenames[i]);
    }
    DecoderManager *manager = DecoderManager_New();
    DecoderManager_Prepare(manager, numDecoder, filenames, argv[4]);
    DecoderManager_Initialize_Range(manager, numDecoder, filenames, argv[4], 59, 62);
    //DecoderManager_Initialize(manager, numDecoder, filenames, argv[4]);
    
    FILE *fp;
    char filename1[1024];
    sprintf(filename1, "%s/input.json", argv[4]);
	fp = fopen(filename1, "w");
    fprintf(fp, "{\n");        
    for(int i=0; i < numDecoder; i++){
        fprintf(fp, "\t  \"Video %d\" : {\n", i);
        fprintf(fp, "\t\t  \"Frame Number\" : %ld,\n", DecoderManager_GetNumFrame(manager));
        fprintf(fp, "\t\t  \"Frame rate \" : %.03f\n", DecoderManager_GetFrameRate(manager));
        fprintf(fp, "\t}");
        if(i != numDecoder - 1){
            fprintf(fp, ",");
        }
        fprintf(fp, "\n");
        
    }
    fprintf(fp, "}");
    fclose(fp);
    DecoderManager_DoDecoding(manager);

    printf("%d, %d\n", DecoderManager_GetStartFrame(manager), DecoderManager_GetEndFrame(manager));
    for (int i = 0; i < numDecoder; i++) {
        delete[]filenames[i];
    }
    delete[]filenames;

    DecoderManager_Finalize(manager);
    return 0;
}
// 프로그램 실행: <Ctrl+F5> 또는 [디버그] > [디버깅하지 않고 시작] 메뉴
// 프로그램 디버그: <F5> 키 또는 [디버그] > [디버깅 시작] 메뉴

// 시작을 위한 팁: 
//   1. [솔루션 탐색기] 창을 사용하여 파일을 추가/관리합니다.
//   2. [팀 탐색기] 창을 사용하여 소스 제어에 연결합니다.
//   3. [출력] 창을 사용하여 빌드 출력 및 기타 메시지를 확인합니다.
//   4. [오류 목록] 창을 사용하여 오류를 봅니다.
//   5. [프로젝트] > [새 항목 추가]로 이동하여 새 코드 파일을 만들거나, [프로젝트] > [기존 항목 추가]로 이동하여 기존 코드 파일을 프로젝트에 추가합니다.
//   6. 나중에 이 프로젝트를 다시 열려면 [파일] > [열기] > [프로젝트]로 이동하고 .sln 파일을 선택합니다.
