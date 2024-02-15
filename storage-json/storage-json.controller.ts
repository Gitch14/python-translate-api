import { Body, Controller, HttpCode, Post } from '@nestjs/common';
import { StorageJSONService } from './storage-json.service';

@Controller('storage/json')
export class StorageJSONController {
  constructor(private storageJSONService: StorageJSONService) {}

  @Post('/')
  @HttpCode(200)
  create(@Body() data: JSON): string | Buffer {
    return this.storageJSONService.saveJSON(data);
  }
}
